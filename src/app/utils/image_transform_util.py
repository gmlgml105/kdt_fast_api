import io
import torch
from torchvision import transforms
from PIL import Image

# 학습했을 때 이미지를 전처리했던 방식과 동일하게 transforms을 생성
def transform_image_alexnet(image_bytes: bytes) -> torch.Tensor:
    my_transforms = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
        mean = [0.485, 0.456, 0.406],
        std = [0.229, 0.224, 0.225]
        )
    ])

    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    tensor = my_transforms(image)
    # 화면 쪽에서 이미지를 등록할건데 차수가 안 맞아서 맞춰줘야 함!
    # [3, 224, 224] -> [3, 224, 224]
    return tensor.unsqueeze(0)



