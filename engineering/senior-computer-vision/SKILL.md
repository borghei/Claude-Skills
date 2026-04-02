---
name: senior-computer-vision
description: >
  Computer vision engineering skill for object detection, image segmentation,
  and visual AI systems. Covers CNN and Vision Transformer architectures,
  YOLO/Faster R-CNN/DETR detection, Mask R-CNN/SAM segmentation, and production
  deployment with ONNX/TensorRT. Includes PyTorch, torchvision, Ultralytics,
  Detectron2, and MMDetection frameworks. Use when building detection pipelines,
  training custom models, optimizing inference, or deploying vision systems.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: computer-vision
  updated: 2026-03-31
  tags: [object-detection, image-segmentation, computer-vision, model-training]
---
# Senior Computer Vision Engineer

The agent designs end-to-end computer vision pipelines for object detection, instance/semantic segmentation, and production deployment. It generates training configurations for YOLO/Detectron2/MMDetection, optimizes models for ONNX/TensorRT/OpenVINO runtimes, and builds dataset preparation workflows with format conversion and augmentation.

## Quick Start

```bash
# Generate training configuration for YOLO or Faster R-CNN
python scripts/vision_model_trainer.py models/ --task detection --arch yolov8

# Analyze model for optimization opportunities (quantization, pruning)
python scripts/inference_optimizer.py model.pt --target onnx --benchmark

# Build dataset pipeline with augmentations
python scripts/dataset_pipeline_builder.py images/ --format coco --augment
```

---

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
# COCO format (recommended)
python scripts/dataset_pipeline_builder.py data/images/ \
    --annotations data/labels/ \
    --format coco \
    --split 0.8 0.1 0.1 \
    --output data/coco/

# Verify dataset
python -c "from pycocotools.coco import COCO; coco = COCO('data/coco/train.json'); print(f'Images: {len(coco.imgs)}, Categories: {len(coco.cats)}')"
```

### Step 4: Configure Training

Generate training configuration:

```bash
# For Ultralytics YOLO
python scripts/vision_model_trainer.py data/coco/ \
    --task detection \
    --arch yolov8m \
    --epochs 100 \
    --batch 16 \
    --imgsz 640 \
    --output configs/

# For Detectron2
python scripts/vision_model_trainer.py data/coco/ \
    --task detection \
    --arch faster_rcnn_R_50_FPN \
    --framework detectron2 \
    --output configs/
```

### Step 5: Train and Validate

```bash
# Ultralytics training
yolo detect train data=data.yaml model=yolov8m.pt epochs=100 imgsz=640

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
# Export with dynamic batch size
python scripts/inference_optimizer.py model.pt \
    --export onnx \
    --input-size 640 640 \
    --dynamic-batch \
    --simplify \
    --output model.onnx

# Verify ONNX model
python -c "import onnx; model = onnx.load('model.onnx'); onnx.checker.check_model(model); print('ONNX model valid')"
```

### Step 4: Apply Quantization (Optional)

For INT8 quantization with calibration:

```bash
# Generate calibration dataset
python scripts/inference_optimizer.py model.onnx \
    --quantize int8 \
    --calibration-data data/calibration/ \
    --calibration-samples 500 \
    --output model_int8.onnx
```

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

# OpenVINO (Intel)
mo --input_model model.onnx --output_dir openvino/

# CoreML (Apple)
python -c "import coremltools as ct; model = ct.convert('model.onnx'); model.save('model.mlpackage')"
```

### Step 6: Benchmark Optimized Model

```bash
python scripts/inference_optimizer.py model.engine \
    --benchmark \
    --runtime tensorrt \
    --compare model.pt
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
python scripts/dataset_pipeline_builder.py data/raw/ \
    --analyze \
    --output analysis/
```

Analysis report includes:

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
# Remove corrupted and duplicate images
python scripts/dataset_pipeline_builder.py data/raw/ \
    --clean \
    --remove-corrupted \
    --remove-duplicates \
    --output data/cleaned/
```

### Step 3: Convert Annotation Format

```bash
# Convert VOC to COCO format
python scripts/dataset_pipeline_builder.py data/cleaned/ \
    --annotations data/annotations/ \
    --input-format voc \
    --output-format coco \
    --output data/coco/
```

Supported format conversions:

| From | To |
|------|-----|
| Pascal VOC XML | COCO JSON |
| YOLO TXT | COCO JSON |
| COCO JSON | YOLO TXT |
| LabelMe JSON | COCO JSON |
| CVAT XML | COCO JSON |

### Step 4: Apply Augmentations

```bash
# Generate augmentation config
python scripts/dataset_pipeline_builder.py data/coco/ \
    --augment \
    --aug-config configs/augmentation.yaml \
    --output data/augmented/
```

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
python scripts/dataset_pipeline_builder.py data/augmented/ \
    --split 0.8 0.1 0.1 \
    --stratify \
    --seed 42 \
    --output data/final/
```

Split strategy guidelines:

| Dataset Size | Train | Val | Test |
|--------------|-------|-----|------|
| <1,000 images | 70% | 15% | 15% |
| 1,000-10,000 | 80% | 10% | 10% |
| >10,000 | 90% | 5% | 5% |

### Step 6: Generate Dataset Configuration

```bash
# For Ultralytics YOLO
python scripts/dataset_pipeline_builder.py data/final/ \
    --generate-config yolo \
    --output data.yaml

# For Detectron2
python scripts/dataset_pipeline_builder.py data/final/ \
    --generate-config detectron2 \
    --output detectron2_config.py
```

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

## Reference Documentation

### 1. Computer Vision Architectures

See `references/computer_vision_architectures.md` for:

- CNN backbone architectures (ResNet, EfficientNet, ConvNeXt)
- Vision Transformer variants (ViT, DeiT, Swin)
- Detection heads (anchor-based vs anchor-free)
- Feature Pyramid Networks (FPN, BiFPN, PANet)
- Neck architectures for multi-scale detection

### 2. Object Detection Optimization

See `references/object_detection_optimization.md` for:

- Non-Maximum Suppression variants (NMS, Soft-NMS, DIoU-NMS)
- Anchor optimization and anchor-free alternatives
- Loss function design (focal loss, GIoU, CIoU, DIoU)
- Training strategies (warmup, cosine annealing, EMA)
- Data augmentation for detection (mosaic, mixup, copy-paste)

### 3. Production Vision Systems

See `references/production_vision_systems.md` for:

- ONNX export and optimization
- TensorRT deployment pipeline
- Batch inference optimization
- Edge device deployment (Jetson, Intel NCS)
- Model serving with Triton
- Video processing pipelines

## Common Commands

### Ultralytics YOLO

```bash
# Training
yolo detect train data=coco.yaml model=yolov8m.pt epochs=100 imgsz=640

# Validation
yolo detect val model=best.pt data=coco.yaml

# Inference
yolo detect predict model=best.pt source=images/ save=True

# Export
yolo export model=best.pt format=onnx simplify=True dynamic=True
```

### Detectron2

```bash
# Training
python train_net.py --config-file configs/COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml \
    --num-gpus 1 OUTPUT_DIR ./output

# Evaluation
python train_net.py --config-file configs/faster_rcnn.yaml --eval-only \
    MODEL.WEIGHTS output/model_final.pth

# Inference
python demo.py --config-file configs/faster_rcnn.yaml \
    --input images/*.jpg --output results/ \
    --opts MODEL.WEIGHTS output/model_final.pth
```

### MMDetection

```bash
# Training
python tools/train.py configs/faster_rcnn/faster-rcnn_r50_fpn_1x_coco.py

# Testing
python tools/test.py configs/faster_rcnn.py checkpoints/latest.pth --eval bbox

# Inference
python demo/image_demo.py demo.jpg configs/faster_rcnn.py checkpoints/latest.pth
```

### Model Optimization

```bash
# ONNX export and simplify
python -c "import torch; model = torch.load('model.pt'); torch.onnx.export(model, torch.randn(1,3,640,640), 'model.onnx', opset_version=17)"
python -m onnxsim model.onnx model_sim.onnx

# TensorRT conversion
trtexec --onnx=model.onnx --saveEngine=model.engine --fp16 --workspace=4096

# Benchmark
trtexec --loadEngine=model.engine --batch=1 --iterations=1000 --avgRuns=100
```

## Performance Targets

| Metric | Real-time | High Accuracy | Edge |
|--------|-----------|---------------|------|
| FPS | >30 | >10 | >15 |
| mAP@50 | >0.6 | >0.8 | >0.5 |
| Latency P99 | <50ms | <150ms | <100ms |
| GPU Memory | <4GB | <8GB | <2GB |
| Model Size | <50MB | <200MB | <20MB |

## Resources

- **Architecture Guide**: `references/computer_vision_architectures.md`
- **Optimization Guide**: `references/object_detection_optimization.md`
- **Deployment Guide**: `references/production_vision_systems.md`
- **Scripts**: `scripts/` directory for automation tools

## Anti-Patterns

- **Training without data audit** -- skipping `dataset_pipeline_builder.py analyze` leads to corrupted images, duplicate pairs, and class imbalance surprises mid-training
- **Deploying FP32 to production** -- always export to FP16 minimum; FP32 wastes 2x memory and 1.5-2x latency for <0.5% mAP difference
- **Ignoring calibration dataset** -- INT8 quantization with random samples causes 5-10% mAP drop; use 500+ representative images from the training distribution
- **One-size-fits-all architecture** -- using YOLOv8x for edge deployment or YOLOv8n for high-accuracy requirements; match architecture to deployment target
- **Benchmarking without warmup** -- first N inference calls include JIT compilation overhead; always use `--warmup 10` for accurate measurements
- **Skipping ONNX validation** -- export can silently produce incorrect models; always run `onnx.checker.check_model()` after export

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Model exports to ONNX but TensorRT conversion fails | Unsupported ONNX opset version or dynamic shapes | Pin `--opset_version 17`, replace dynamic axes with fixed sizes, and run `python -m onnxsim model.onnx model_sim.onnx` before TensorRT conversion |
| mAP drops significantly after INT8 quantization | Calibration dataset is too small or unrepresentative | Use at least 500 representative images from the training distribution for calibration; verify per-class AP to find affected classes |
| Training loss plateaus early without convergence | Learning rate too high, insufficient augmentation, or frozen backbone layers | Reduce `lr0` by 10x, enable mosaic/mixup augmentation, and unfreeze backbone (`--freeze None`) after initial warmup |
| CUDA out-of-memory during training | Batch size or image resolution too large for available VRAM | Halve `--batch`, reduce `--imgsz` to 512, enable `--amp True` for mixed precision, or use gradient accumulation via `--nbs` |
| High false-positive rate on small objects | Default anchor sizes miss small targets; NMS threshold too permissive | Use SAHI (Slicing Aided Hyper Inference), add FPN levels for small scales, and tighten `conf` threshold to 0.4+ |
| Annotation format conversion produces empty labels | Coordinate system mismatch (absolute vs normalized) or category ID mapping errors | Run `dataset_pipeline_builder.py validate` before and after conversion; check that bounding box values are within image dimensions |
| Inference FPS is lower than expected on GPU | CPU-bound pre/post-processing bottleneck, no batch processing, or missing CUDA warmup | Profile with `--benchmark --warmup 10`, move pre-processing to GPU (torchvision transforms), and ensure `torch.cuda.synchronize()` is called correctly |

## Success Criteria

- **Detection accuracy**: mAP@50 above 0.70 and mAP@50:95 above 0.50 on the target validation set
- **Inference latency**: P99 latency under 50ms per frame at batch size 1 on target hardware for real-time deployments
- **Throughput**: Sustained processing above 30 FPS for real-time pipelines, above 10 FPS for high-accuracy pipelines
- **Model size**: Optimized model under 50MB for edge deployment, under 200MB for cloud GPU deployment
- **Quantization fidelity**: Less than 2% mAP drop when moving from FP32 to FP16; less than 3% drop for INT8
- **Dataset quality**: Class imbalance ratio no worse than 1:10 between least and most frequent classes; zero corrupted images; annotation coverage above 95% of images
- **Deployment reliability**: ONNX model passes `onnx.checker.check_model()` validation; TensorRT engine builds without warnings on target GPU architecture

## Scope & Limitations

**This skill covers:**

- End-to-end object detection and segmentation pipeline design (data preparation through production deployment)
- Training configuration generation for Ultralytics YOLO, Detectron2, and MMDetection frameworks
- Model optimization and export to ONNX, TensorRT, OpenVINO, and CoreML runtimes
- Dataset format conversion (COCO, YOLO, Pascal VOC, CVAT), splitting, validation, and augmentation configuration

**This skill does NOT cover:**

- Generative vision tasks (image generation, style transfer, super-resolution) -- see dedicated generative AI skills
- 3D reconstruction, SLAM, or point cloud processing beyond basic depth estimation
- Medical imaging regulatory compliance (DICOM, FDA 510(k)) -- see `ra-qm-team/` compliance skills
- Real-time video streaming infrastructure (RTSP, WebRTC, GStreamer pipeline design) -- see `senior-devops` for infrastructure

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `senior-ml-engineer` | Model serving and MLOps pipeline setup | Trained model artifacts (.pt, .onnx) flow into `model_deployment_pipeline.py` for containerized serving and monitoring |
| `senior-data-engineer` | Dataset ETL and storage pipelines | Raw image data ingested via `pipeline_orchestrator.py`; cleaned datasets flow into `dataset_pipeline_builder.py` for CV formatting |
| `senior-data-scientist` | Experiment design and statistical analysis | Experiment parameters from `experiment_designer.py` guide hyperparameter search; model metrics feed back for significance testing |
| `senior-devops` | CI/CD and GPU infrastructure provisioning | Optimized model artifacts deployed via CI/CD pipelines; GPU node scaling managed through infrastructure-as-code |
| `senior-prompt-engineer` | Multimodal RAG and vision-language integration | Vision model embeddings and detections feed into `rag_system_builder.py` for multimodal retrieval pipelines |
| `senior-cloud-architect` | Cloud GPU resource planning and cost optimization | Benchmark results from `inference_optimizer.py` inform instance type selection and auto-scaling policies |

## Tool Reference

### vision_model_trainer.py

**Purpose:** Generates training configuration files for object detection and segmentation models across Ultralytics YOLO, Detectron2, and MMDetection frameworks.

**Usage:**

```bash
python scripts/vision_model_trainer.py <data_dir> [options]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data_dir` | positional | (required) | Path to dataset directory |
| `--task` | choice | `detection` | Task type: `detection`, `segmentation` |
| `--framework` | choice | `ultralytics` | Training framework: `ultralytics`, `detectron2`, `mmdetection` |
| `--arch` | string | `yolov8m` | Model architecture (e.g., `yolov8n`, `yolov8s`, `yolov8m`, `yolov8l`, `yolov8x`, `yolov5n`-`yolov5x`, `faster_rcnn_R_50_FPN`, `mask_rcnn_R_50_FPN`, `retinanet_R_50_FPN`, `detr_r50`, `dino_r50`, `yolox_s`/`m`/`l`) |
| `--epochs` | int | `100` | Number of training epochs |
| `--batch` | int | `16` | Batch size |
| `--imgsz` | int | `640` | Input image size (Ultralytics only) |
| `--output`, `-o` | string | None | Output config file path |
| `--analyze-only` | flag | off | Only analyze dataset structure, skip config generation |
| `--json` | flag | off | Output results as JSON |

**Example:**

```bash
# Generate Ultralytics YOLO training config
python scripts/vision_model_trainer.py data/coco/ --task detection --arch yolov8m --epochs 100 --batch 16 --output configs/train.yaml

# Analyze dataset only
python scripts/vision_model_trainer.py data/coco/ --analyze-only --json

# Generate Detectron2 config
python scripts/vision_model_trainer.py data/coco/ --framework detectron2 --arch faster_rcnn_R_50_FPN --output configs/detectron2.py
```

**Output Formats:**

- **Human-readable** (default): Prints a summary table with framework, architecture, parameters, COCO mAP, and the training command
- **JSON** (`--json`): Full configuration dictionary including all hyperparameters and metadata
- **Config file** (`--output`): YAML for Ultralytics; Python config for Detectron2/MMDetection

---

### inference_optimizer.py

**Purpose:** Analyzes model structure, benchmarks inference speed across batch sizes, and provides optimization recommendations for target deployment platforms.

**Usage:**

```bash
python scripts/inference_optimizer.py <model_path> [options]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_path` | positional | (required) | Path to model file (`.pt`, `.pth`, `.onnx`, `.engine`, `.trt`, `.xml`, `.mlpackage`, `.mlmodel`) |
| `--analyze` | flag | off | Analyze model structure (parameters, layers, input/output shapes) |
| `--benchmark` | flag | off | Benchmark inference speed |
| `--input-size` | int int | `640 640` | Input image size as H W |
| `--batch-sizes` | int list | `1 4 8` | Batch sizes to benchmark |
| `--iterations` | int | `100` | Number of benchmark iterations |
| `--warmup` | int | `10` | Number of warmup iterations before benchmarking |
| `--target` | choice | `gpu` | Target deployment platform: `gpu`, `cpu`, `edge`, `mobile`, `apple`, `intel` |
| `--recommend` | flag | off | Show optimization recommendations for the target platform |
| `--json` | flag | off | Output results as JSON |
| `--output`, `-o` | string | None | Save results to file |

**Example:**

```bash
# Analyze model structure
python scripts/inference_optimizer.py model.onnx --analyze

# Benchmark with custom batch sizes
python scripts/inference_optimizer.py model.pt --benchmark --input-size 640 640 --batch-sizes 1 4 8 16 --warmup 10 --iterations 100

# Get optimization recommendations for edge deployment
python scripts/inference_optimizer.py model.pt --analyze --recommend --target edge --json

# Save full report
python scripts/inference_optimizer.py model.onnx --analyze --benchmark --recommend --output report.json
```

**Output Formats:**

- **Human-readable** (default): Summary table with file size, parameters, node count; benchmark table with latency, throughput, and P99 per batch size; numbered optimization recommendations with expected speedup
- **JSON** (`--json`): Nested dictionary with `analysis`, `benchmark`, and `recommendations` keys
- **File** (`--output`): JSON report saved to specified path

---

### dataset_pipeline_builder.py

**Purpose:** Production-grade tool for analyzing, converting, splitting, augmenting, and validating computer vision datasets. Uses subcommands for each operation.

**Usage:**

```bash
python scripts/dataset_pipeline_builder.py <command> [options]
```

**Subcommands:**

#### `analyze` -- Analyze dataset structure and statistics

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--input`, `-i` | string | (required) | Path to dataset |
| `--json` | flag | off | Output as JSON |

```bash
python scripts/dataset_pipeline_builder.py analyze --input data/coco/
python scripts/dataset_pipeline_builder.py analyze --input data/coco/ --json
```

#### `convert` -- Convert between annotation formats

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--input`, `-i` | string | (required) | Input dataset path |
| `--output`, `-o` | string | (required) | Output dataset path |
| `--format`, `-f` | choice | (required) | Target format: `yolo`, `coco`, `voc` |
| `--source-format`, `-s` | choice | None | Source format: `yolo`, `coco`, `voc` (auto-detected if omitted) |

```bash
python scripts/dataset_pipeline_builder.py convert --input data/voc/ --output data/coco/ --format coco
python scripts/dataset_pipeline_builder.py convert --input data/coco/ --output data/yolo/ --format yolo --source-format coco
```

#### `split` -- Split dataset into train/val/test sets

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--input`, `-i` | string | (required) | Input dataset path |
| `--output`, `-o` | string | same as input | Output path |
| `--train` | float | `0.8` | Train split ratio |
| `--val` | float | `0.1` | Validation split ratio |
| `--test` | float | `0.1` | Test split ratio |
| `--stratify` | flag | off | Stratify splits by class distribution |
| `--seed` | int | `42` | Random seed for reproducibility |

```bash
python scripts/dataset_pipeline_builder.py split --input data/coco/ --train 0.8 --val 0.1 --test 0.1 --stratify --seed 42
```

#### `augment-config` -- Generate augmentation configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--task`, `-t` | choice | (required) | CV task: `detection`, `segmentation`, `classification` |
| `--intensity`, `-n` | choice | `medium` | Augmentation intensity: `light`, `medium`, `heavy` |
| `--framework`, `-f` | choice | `albumentations` | Target framework: `albumentations`, `torchvision`, `ultralytics` |
| `--output`, `-o` | string | None | Output file path |

```bash
python scripts/dataset_pipeline_builder.py augment-config --task detection --intensity heavy --output augmentations.yaml
```

#### `validate` -- Validate dataset integrity

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--input`, `-i` | string | (required) | Path to dataset |
| `--format`, `-f` | choice | None | Dataset format: `yolo`, `coco`, `voc` (auto-detected if omitted) |
| `--json` | flag | off | Output as JSON |

```bash
python scripts/dataset_pipeline_builder.py validate --input data/coco/ --format coco
```

**Output Formats:**

- **Human-readable** (default): Structured report with dataset statistics, annotation counts, class distributions, quality checks, and actionable recommendations
- **JSON** (`--json`): Full analysis dictionary including image stats, annotation details, bounding box statistics, and quality check results
