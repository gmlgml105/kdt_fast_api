import torch
import torch.nn as nn
import torchvision.models as models
from fastapi import Depends
from pathlib import Path
from app.utils.image_transform_util import transform_image_alexnet

# 싱글턴 패턴
# 서버에서 인스턴스를 1개만 생성하도록 보장하는 패턴
class AiService:

    def __init__(self, weight_path: str = None):
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif torch.mps.is_available():
            self.device = torch.device("mps")
        elif torch.xpu.is_available():
            self.device = torch.device("xpu")
        else:
            self.device = torch.device("cpu")

        self.model = None

        if weight_path is None:
            self.weight_path = Path(__file__).resolve().parent.parent / "weights" / "alexnet_model_weight.pth"
        else:
            self.weight_path = Path(weight_path)

    # 모델 로드
    def load_alexnet_model(self):
        # 1. 사전 학습 모델 뼈대를 다운로드
        self.model = models.alexnet(weights="IMAGENET1K_V1")
        # 2. 분류기(classifier)를 학습한 모델의 분류기 구조로 재정의 
        self.model.classifier = nn.Sequential(
            nn.Linear(256 * 6 * 6, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )

        if not self.weight_path.exists():
            raise FileNotFoundError(f"Weight Path Not Found Error: {self.weight_path}")

        # 3. 저장된 커스텀 가중치 로드
        state_dict = torch.load(str(self.weight_path), map_location=self.device)
        self.model.load_state_dict(state_dict)

        # 4. 디바이스 배치, 평가 모드 전환 
        self.model.to(self.device)
        self.model.eval()


    # 예측 서비스
    def predict_image(self, image_bytes: bytes):
        if self.model is None:
            raise RuntimeError("Model is Not Loaded! predict_image")

        # 1. 이미지를 텐서로 변환
        input_tensor = transform_image_alexnet(image_bytes)

        # 2. 모델 추론
        with torch.no_grad():
            tensor_x = input_tensor.to(self.device)
            output = self.model(tensor_x) # 0 ~ 1
            score = output.item()

        label = "Dog(강아지)" if score >= 0.5 else "Cat(고양이)"

        # 이미지 저장
        # DB 저장 경로 + 확률 + top-k
        # top-k : JSONB

        # 3. 결과를 원하는 형태로 반환 
        return {
            "label": label,
            "probability": score,
            "raw_output": output.tolist()
        }

ai_service_instance = AiService()

def get_ai_service() -> AiService:
    return ai_service_instance