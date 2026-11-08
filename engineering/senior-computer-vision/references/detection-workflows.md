# Computer Vision Workflows & Architecture Selection

Read this when building a detection pipeline, optimizing/deploying a model, preparing a dataset, or selecting an architecture — quick-start commands, the three end-to-end workflows, and the architecture selection guide.

## Quick Start

```bash
# Generate training configuration for YOLO or Faster R-CNN
python scripts/vision_model_trainer.py models/ --task detection --arch yolo26m

# Analyze model for optimization opportunities (quantization, pruning)
python scripts/inference_optimizer.py model.pt --analyze --benchmark --recommend --target gpu

# Validate a dataset, then generate an augmentation config
python scripts/dataset_pipeline_builder.py validate --input data/coco/ --format coco
python scripts/dataset_pipeline_builder.py augment-config --task detection --intensity medium
```

## Workflow 1: Object Detection Pipeline

The agent uses this workflow when building an object detection system from scratch.

### Step 1: Define Detection Requirements

Analyze the detection task requirements:

```
Detection Requirements Analysis:
- Target objects: [list specific classes to detect]
- Real-time requirement: [yes/no, target FPS]
- Accuracy priority: [speed vs accuracy trade-off]
- Deployment target: [cloud GPU, edge device, mobile]
- Dataset size: [number of images, annotations per class]
```

### Step 2: Select Detection Architecture

Choose architecture based on requirements:

| Requirement | Recommended Architecture | Why |
|-------------|-------------------------|-----|
| Real-time (>30 FPS) | YOLOv8/v11, RT-DETR | Single-stage, optimized for speed |
| High accuracy | Faster R-CNN, DINO | Two-stage, better localization |
| Small objects | YOLO + SAHI, Faster R-CNN + FPN | Multi-scale detection |
| Edge deployment | YOLOv8n, MobileNetV3-SSD | Lightweight architectures |
| Transformer-based | DETR, DINO, RT-DETR | End-to-end, no NMS required |

### Step 3: Prepare Dataset

Convert annotations to required format:

```bash
# Convert to COCO (recommended), then split
python scripts/dataset_pipeline_builder.py convert --input data/labels/ --output data/coco/ --format coco
python scripts/dataset_pipeline_builder.py split --input data/coco/ --train 0.8 --val 0.1 --test 0.1 --stratify

# Verify dataset
python -c "from pycocotools.coco import COCO; coco = COCO('data/coco/train.json'); print(f'Images: {len(coco.imgs)}, Categories: {len(coco.cats)}')"
```

### Step 4: Configure Training

Generate training configuration:

```bash
# For Ultralytics YOLO
python scripts/vision_model_trainer.py data/coco/ \
    --task detection \
    --arch yolo26m \
    --epochs 100 \
    --batch 16 \
    --imgsz 640 \
    --output configs/train.yaml

# For Detectron2
python scripts/vision_model_trainer.py data/coco/ \
    --task detection \
    --arch faster_rcnn_R_50_FPN \
    --framework detectron2 \
    --output configs/detectron2.py
```

### Step 5: Train and Validate

```bash
# Ultralytics training
yolo detect train data=data.yaml model=yolo26m.pt epochs=100 imgsz=640

# Detectron2 training
python train_net.py --config-file configs/faster_rcnn.yaml --num-gpus 1

# Validate on test set
yolo detect val model=runs/detect/train/weights/best.pt data=data.yaml
```

### Step 6: Evaluate Results

Key metrics to analyze:

| Metric | Target | Description |
|--------|--------|-------------|
| mAP@50 | >0.7 | Mean Average Precision at IoU 0.5 |
| mAP@50:95 | >0.5 | COCO primary metric |
| Precision | >0.8 | Low false positives |
| Recall | >0.8 | Low missed detections |
| Inference time | <33ms | For 30 FPS real-time |

## Workflow 2: Model Optimization and Deployment

Use this workflow when preparing a trained model for production deployment.

### Step 1: Benchmark Baseline Performance

```bash
# Measure current model performance
python scripts/inference_optimizer.py model.pt \
    --benchmark \
    --input-size 640 640 \
    --batch-sizes 1 4 8 16 \
    --warmup 10 \
    --iterations 100
```

Expected output:

```
Baseline Performance (PyTorch FP32):
- Batch 1: 45.2ms (22.1 FPS)
- Batch 4: 89.4ms (44.7 FPS)
- Batch 8: 165.3ms (48.4 FPS)
- Memory: 2.1 GB
- Parameters: 25.9M
```

### Step 2: Select Optimization Strategy

| Deployment Target | Optimization Path |
|-------------------|-------------------|
| NVIDIA GPU (cloud) | PyTorch → ONNX → TensorRT FP16 |
| NVIDIA GPU (edge) | PyTorch → TensorRT INT8 |
| Intel CPU | PyTorch → ONNX → OpenVINO |
| Apple Silicon | PyTorch → CoreML |
| Generic CPU | PyTorch → ONNX Runtime |
| Mobile | PyTorch → TFLite or ONNX Mobile |

### Step 3: Export to ONNX

```bash
# Export with dynamic batch size (Ultralytics models; use torch.onnx.export for others).
# inference_optimizer.py analyses and recommends; it does not export.
yolo export model=model.pt format=onnx imgsz=640 dynamic=True simplify=True

# Verify ONNX model
python -c "import onnx; model = onnx.load('model.onnx'); onnx.checker.check_model(model); print('ONNX model valid')"
```

### Step 4: Apply Quantization (Optional)

For INT8 quantization with calibration:

Use `onnxruntime.quantization.quantize_static` with a calibration data reader over roughly
500 representative images (or TensorRT's INT8 calibrator via `trtexec --int8 --calib=...`).
Validate mAP on the held-out set after quantizing; accept the model only if the drop is
within the budget agreed in Clarify First.

Quantization impact analysis:

| Precision | Size | Speed | Accuracy Drop |
|-----------|------|-------|---------------|
| FP32 | 100% | 1x | 0% |
| FP16 | 50% | 1.5-2x | <0.5% |
| INT8 | 25% | 2-4x | 1-3% |

### Step 5: Convert to Target Runtime

```bash
# TensorRT (NVIDIA GPU)
trtexec --onnx=model.onnx --saveEngine=model.engine --fp16

# OpenVINO (Intel) - `ovc` replaced the older `mo` Model Optimizer
ovc model.onnx --output_model openvino/model.xml

# CoreML (Apple) - coremltools converts from PyTorch, not ONNX
yolo export model=model.pt format=coreml
```

### Step 6: Benchmark Optimized Model

```bash
# TensorRT engine latency
trtexec --loadEngine=model.engine --iterations=200

# ONNX vs PyTorch with the bundled tool (needs onnxruntime / torch installed)
python scripts/inference_optimizer.py model.onnx --benchmark --batch-sizes 1 8
python scripts/inference_optimizer.py model.pt --benchmark --batch-sizes 1 8
```

Expected speedup:

```
Optimization Results:
- Original (PyTorch FP32): 45.2ms
- Optimized (TensorRT FP16): 12.8ms
- Speedup: 3.5x
- Accuracy change: -0.3% mAP
```

## Workflow 3: Custom Dataset Preparation

Use this workflow when preparing a computer vision dataset for training.

### Step 1: Audit Raw Data

```bash
# Analyze image dataset
python scripts/dataset_pipeline_builder.py analyze --input data/raw/ --json > analysis.json
```

An audit should establish (fill gaps the tool does not report by hand):

```
Dataset Analysis:
- Total images: 5,234
- Image sizes: 640x480 to 4096x3072 (variable)
- Formats: JPEG (4,891), PNG (343)
- Corrupted: 12 files
- Duplicates: 45 pairs

Annotation Analysis:
- Format detected: Pascal VOC XML
- Total annotations: 28,456
- Classes: 5 (car, person, bicycle, dog, cat)
- Distribution: car (12,340), person (8,234), bicycle (3,456), dog (2,890), cat (1,536)
- Empty images: 234
```

### Step 2: Clean and Validate

```bash
# Report broken references, bad boxes and unknown categories (exit 1 when any error is found).
# The tool does not delete files: remove corrupted or duplicate images yourself, then re-run.
python scripts/dataset_pipeline_builder.py validate --input data/raw/
```

### Step 3: Convert Annotation Format

```bash
# Convert VOC to COCO format
python scripts/dataset_pipeline_builder.py convert --input data/cleaned/ --output data/coco/ \
    --format coco --source-format voc
```

Supported format conversions:

| From | To |
|------|-----|
| Pascal VOC XML | COCO JSON |
| YOLO TXT | COCO JSON |
| COCO JSON | YOLO TXT |

### Step 4: Apply Augmentations

```bash
# Generate augmentation config
python scripts/dataset_pipeline_builder.py augment-config --task detection --intensity medium \
    --framework albumentations --output configs/augmentation.json
```

The tool writes a config, it does not augment images; apply augmentations online in the
training framework rather than materialising an augmented copy of the dataset.

Recommended augmentations for detection:

```yaml
# configs/augmentation.yaml
augmentations:
  geometric:
    - horizontal_flip: { p: 0.5 }
    - vertical_flip: { p: 0.1 }  # Only if orientation invariant
    - rotate: { limit: 15, p: 0.3 }
    - scale: { scale_limit: 0.2, p: 0.5 }

  color:
    - brightness_contrast: { brightness_limit: 0.2, contrast_limit: 0.2, p: 0.5 }
    - hue_saturation: { hue_shift_limit: 20, sat_shift_limit: 30, p: 0.3 }
    - blur: { blur_limit: 3, p: 0.1 }

  advanced:
    - mosaic: { p: 0.5 }  # YOLO-style mosaic
    - mixup: { p: 0.1 }   # Image mixing
    - cutout: { num_holes: 8, max_h_size: 32, max_w_size: 32, p: 0.3 }
```

### Step 5: Create Train/Val/Test Splits

```bash
python scripts/dataset_pipeline_builder.py split --input data/coco/ --output data/final/ \
    --train 0.8 --val 0.1 --test 0.1 --stratify --seed 42
```

Split strategy guidelines:

| Dataset Size | Train | Val | Test |
|--------------|-------|-----|------|
| <1,000 images | 70% | 15% | 15% |
| 1,000-10,000 | 80% | 10% | 10% |
| >10,000 | 90% | 5% | 5% |

### Step 6: Generate Dataset Configuration

The tools do not write dataset configs. For Ultralytics, write `data.yaml` by hand
(`path`, `train`, `val`, `test`, `names`); `vision_model_trainer.py` reads its `names` list.
For Detectron2, register the COCO splits with `register_coco_instances` in your train script.

## Architecture Selection Guide

### Object Detection Architectures

| Architecture | Speed | Accuracy | Best For |
|--------------|-------|----------|----------|
| YOLOv8n | 1.2ms | 37.3 mAP | Edge, mobile, real-time |
| YOLOv8s | 2.1ms | 44.9 mAP | Balanced speed/accuracy |
| YOLOv8m | 4.2ms | 50.2 mAP | General purpose |
| YOLOv8l | 6.8ms | 52.9 mAP | High accuracy |
| YOLOv8x | 10.1ms | 53.9 mAP | Maximum accuracy |
| RT-DETR-L | 5.3ms | 53.0 mAP | Transformer, no NMS |
| Faster R-CNN R50 | 46ms | 40.2 mAP | Two-stage, high quality |
| DINO-4scale | 85ms | 49.0 mAP | SOTA transformer |

### Segmentation Architectures

| Architecture | Type | Speed | Best For |
|--------------|------|-------|----------|
| YOLOv8-seg | Instance | 4.5ms | Real-time instance seg |
| Mask R-CNN | Instance | 67ms | High-quality masks |
| SAM | Promptable | 50ms | Zero-shot segmentation |
| DeepLabV3+ | Semantic | 25ms | Scene parsing |
| SegFormer | Semantic | 15ms | Efficient semantic seg |

### CNN vs Vision Transformer Trade-offs

| Aspect | CNN (YOLO, R-CNN) | ViT (DETR, DINO) |
|--------|-------------------|------------------|
| Training data needed | 1K-10K images | 10K-100K+ images |
| Training time | Fast | Slow (needs more epochs) |
| Inference speed | Faster | Slower |
| Small objects | Good with FPN | Needs multi-scale |
| Global context | Limited | Excellent |
| Positional encoding | Implicit | Explicit |
