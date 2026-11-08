# Tool Reference

Read this when you need the full parameter reference, examples, and output formats for the computer-vision automation scripts.

## vision_model_trainer.py

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
| `--arch` | string | `yolo26m` | Model architecture (e.g., `yolo26n`-`yolo26m`, `yolo11n`-`yolo11x`, `yolov8n`-`yolov8x`, `yolov5n`-`yolov5x`, `faster_rcnn_R_50_FPN`, `mask_rcnn_R_50_FPN`, `retinanet_R_50_FPN`, `detr_r50`, `dino_r50`, `yolox_s`/`m`/`l`) |
| `--epochs` | int | `100` | Number of training epochs |
| `--batch` | int | `16` | Batch size |
| `--imgsz` | int | `640` | Input image size (Ultralytics only) |
| `--output`, `-o` | string | None | Output config file path |
| `--analyze-only` | flag | off | Only analyze dataset structure, skip config generation |
| `--json` | flag | off | Output results as JSON |

**Example:**

```bash
# Generate Ultralytics YOLO training config
python scripts/vision_model_trainer.py data/coco/ --task detection --arch yolo26m --epochs 100 --batch 16 --output configs/train.yaml

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

## inference_optimizer.py

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

## dataset_pipeline_builder.py

**Purpose:** Production-grade tool for analyzing, converting, splitting, augmenting, and validating computer vision datasets. Uses subcommands for each operation.

**Usage:**

```bash
python scripts/dataset_pipeline_builder.py <command> [options]
```

**Subcommands:**

### `analyze` -- Analyze dataset structure and statistics

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--input`, `-i` | string | (required) | Path to dataset |
| `--json` | flag | off | Output as JSON |

```bash
python scripts/dataset_pipeline_builder.py analyze --input data/coco/
python scripts/dataset_pipeline_builder.py analyze --input data/coco/ --json
```

### `convert` -- Convert between annotation formats

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

### `split` -- Split dataset into train/val/test sets

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

### `augment-config` -- Generate augmentation configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--task`, `-t` | choice | (required) | CV task: `detection`, `segmentation`, `classification` |
| `--intensity`, `-n` | choice | `medium` | Augmentation intensity: `light`, `medium`, `heavy` |
| `--framework`, `-f` | choice | `albumentations` | Target framework: `albumentations`, `torchvision`, `ultralytics` |
| `--output`, `-o` | string | None | Output file path |

```bash
python scripts/dataset_pipeline_builder.py augment-config --task detection --intensity heavy --output augmentations.json
```

### `validate` -- Validate dataset integrity

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
