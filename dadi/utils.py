import os
import clip
import torch
from torch import nn, optim
from PIL import Image
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import transforms
from tqdm import tqdm
import datetime

# Model and Preprocess
def initialize_model(device, model_name="ViT-B/32"):
    model, preprocess = clip.load(model_name, device=device, jit=False)
    model = model.to(torch.float32)
    return model, preprocess

# Dataset Class
class LocalDataset(Dataset):
    def __init__(self, root_dir, preprocess, transforms):
        self.root_dir = root_dir
        self.preprocess = preprocess
        self.transforms = transforms
        self.samples = []
        self.text_descriptions = []
        self._load_dataset()

    def _load_dataset(self):
        for label in os.listdir(self.root_dir):
            label_dir = os.path.join(self.root_dir, label)
            if os.path.isdir(label_dir):
                for img_filename in os.listdir(label_dir):
                    img_path = os.path.join(label_dir, img_filename)
                    if os.path.isfile(img_path):
                        self.samples.append((img_path, label))
                        text_description = clip.tokenize(f"a remote sensing image of a {label}")
                        self.text_descriptions.append(text_description)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        image = Image.open(img_path).convert('RGB')
        image = self.transforms(image)
        image = self.preprocess(image)
        text = self.text_descriptions[idx]
        return image, text

# Split Dataset
def split_dataset(dataset, train_ratio=0.8):
    train_size = int(len(dataset) * train_ratio)
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
    return train_dataset, val_dataset

# Data Loaders
def create_data_loaders(train_dataset, val_dataset, batch_size):
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    return train_loader, val_loader

# Training Function
def train_model(model, train_loader, optimizer, device, epoch):
    model.train()
    train_total, train_correct = 0, 0
    pbar = tqdm(train_loader, total=len(train_loader))
    for batch in pbar:
        optimizer.zero_grad()
        
        images, texts = batch
        texts = texts.squeeze(1)
        images = images.to(device)
        texts = texts.to(device)
        
    #for images, texts in tqdm(train_loader, total=len(train_loader)):
        #optimizer.zero_grad()
        #images, texts = images.to(device), texts.squeeze(1).to(device)
        logits_per_image, logits_per_text = model(images, texts)
        ground_truth = torch.arange(images.size(0)).to(device)
        total_loss = (nn.CrossEntropyLoss()(logits_per_image, ground_truth) + nn.CrossEntropyLoss()(logits_per_text, ground_truth)) / 2
        total_loss.backward()
        optimizer.step()
        train_correct += (logits_per_image.argmax(dim=1) == ground_truth).float().sum().item()
        train_total += images.size(0)
        train_accuracy = 100 * train_correct / train_total
        pbar.set_description(f"Epoch {epoch+1}/{epoch}, Loss: {total_loss.item():.4f}, Train Acc: {train_accuracy:.2f}%")
    #print(f"Epoch {epoch+1}/{EPOCH}, Train Acc: {train_accuracy:.2f}%")

# Validation Function
def validate_model(model, val_loader, device):
    model.eval()
    val_total, val_correct = 0, 0
    with torch.no_grad():
        pbar_val = tqdm(val_loader, total=len(val_loader))
        for batch in pbar_val:
            images, texts = batch
            texts = texts.squeeze(1)
            images = images.to(device)
            texts = texts.to(device)
            
            
        #for images, texts in tqdm(val_loader, total=len(val_loader)):
            #images, texts = images.to(device), texts.squeeze(1).to(device)
            logits_per_image, _ = model(images, texts)
            ground_truth = torch.arange(images.size(0)).to(device)
            val_correct += (logits_per_image.argmax(dim=1) == ground_truth).float().sum().item()
            val_total += images.size(0)
    val_accuracy = 100 * val_correct / val_total
    print(f"Validation Accuracy: {val_accuracy:.2f}%")
    return val_accuracy

# Main Function
def main():
    model, preprocess = initialize_model(device)
    transforms = get_transforms()
    dataset = LocalDataset(root_dir=DATASET, preprocess=preprocess, transforms=transforms)
    train_dataset, val_dataset = split_dataset(dataset, train_ratio=SPLIT)
    train_loader, val_loader = create_data_loaders(train_dataset, val_dataset, BATCH_SIZE)
    optimizer = torch.optim.SGD(model.parameters(), lr=LR)
    for epoch in range(EPOCH):
        train_model(model, train_loader, optimizer, device, epoch)
        val_accuracy = validate_model(model, val_loader, device)
    now = datetime.datetime.now()
    torch.save(model.state_dict(), f"CLIP-random-cropping-{now}-{val_accuracy:.2f}.pth")

if __name__ == "__main__":
    main()