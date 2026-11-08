---
name: senior-computer-vision
description: >
  Computer vision engineering for object detection, segmentation, and visual AI, covering CNN
  and Vision Transformer architectures and ONNX/TensorRT deployment. Use when building
  detection pipelines, training models, or optimizing inference.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: computer-vision
  updated: 2026-11-08
  tags: [object-detection, image-segmentation, computer-vision, model-training]
---
# Senior Computer Vision Engineer

Design end-to-end computer vision pipelines for object detection, instance/semantic segmentation, and production deployment. Generates training configurations for YOLO/Detectron2/MMDetection, optimizes models for ONNX/TensorRT/OpenVINO runtimes, and builds dataset preparation workflows with format conversion and augmentation.

## Core Capabilities

- **Detection pipeline design** — requirements analysis, architecture selection (YOLO/RT-DETR/Faster R-CNN/DINO), dataset prep, training config, and metric evaluation.
- **Model optimization & deployment** — baseline benchmarking, ONNX export, INT8/FP16 quantization, and conversion to TensorRT/OpenVINO/CoreML/TFLite per target platform.
- **Dataset engineering** — audit, cleaning, format conversion (COCO/YOLO/VOC/CVAT/LabelMe), augmentation config, and stratified train/val/test splits.
- **Architecture guidance** — detection and segmentation architecture trade-offs plus CNN vs Vision Transformer selection.
- **Production targets** — FPS, mAP, latency P99, memory, and model-size budgets for real-time, high-accuracy, and edge deployments.

## When to Use

- Building an object detection or segmentation system from scratch.
- Optimizing and deploying a trained model to GPU, edge, or mobile.
- Preparing, converting, or auditing a computer vision dataset.
- Choosing an architecture for a speed/accuracy/deployment trade-off.

## Clarify First

Before generating training configs or pipelines, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Task:** detection / instance or semantic segmentation / classification (selects the architecture and `--task`).
- **Dataset:** location and format (COCO / YOLO / VOC) to analyze or convert (the input to `dataset_pipeline_builder.py`).
- **Deployment target:** GPU / edge / mobile (drives architecture choice and `inference_optimizer --target`).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Tools

All three are stdlib-only CLIs. `inference_optimizer.py` needs the model's runtime (torch for
`.pt`, onnx/onnxruntime and numpy for `.onnx`) to analyse or benchmark; without it only
format-based recommendations are produced and `--benchmark` exits 2.

| Tool | Purpose | Example (runs as written) |
|------|---------|---------|
| `vision_model_trainer.py` | Analyse a COCO/YOLO dataset and generate a YOLO / Detectron2 / MMDetection training config (`--framework`, `--arch`, `--epochs`, `--batch`, `-o`, `--analyze-only`, `--json`) | `python scripts/vision_model_trainer.py assets/sample_coco_valid --analyze-only --json` |
| `inference_optimizer.py` | Analyse, benchmark and recommend optimisations per target (`--analyze`, `--benchmark`, `--recommend`, `--target gpu/cpu/edge/mobile/apple/intel`, `--json`, `-o`) | `python scripts/inference_optimizer.py model.onnx --analyze --recommend --target edge` |
| `dataset_pipeline_builder.py` | Subcommands `analyze`, `convert`, `split`, `augment-config`, `validate` | `python scripts/dataset_pipeline_builder.py validate --input assets/sample_coco_flawed` |

Exit codes: `0` ok; `1` `validate` found errors (broken image references, malformed boxes);
`2` bad input (missing path, unknown architecture or format) or a requested benchmark that
could not run. `assets/sample_coco_valid/` validates clean (exit 0); `assets/sample_coco_flawed/`
has an orphan annotation and a 3-value bbox (exit 1).

Default recommendation: YOLO26 (Ultralytics' current family; COCO mAP50-95 yolo26n 40.9,
yolo26s 48.6, yolo26m 53.1 per docs.ultralytics.com/models/yolo26/, checked November 2026),
with YOLO11 kept for existing pipelines. The trainer's table cites its source per entry;
check the docs again before quoting figures, since families turn over yearly.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/detection-workflows.md](references/detection-workflows.md)** — quick-start commands and the three end-to-end workflows (detection pipeline, model optimization/deployment, dataset prep) plus the architecture selection guide. Read when executing a pipeline.
- **[references/commands-targets-and-troubleshooting.md](references/commands-targets-and-troubleshooting.md)** — framework command catalogs (YOLO/Detectron2/MMDetection/optimization), performance targets, anti-patterns, troubleshooting table, and success criteria. Read while running training or deployment.
- **[references/tool-reference.md](references/tool-reference.md)** — full parameter, example, and output-format reference for the three scripts. Read when scripting the tools.
- **[references/computer_vision_architectures.md](references/computer_vision_architectures.md)** — CNN backbones (ResNet, EfficientNet, ConvNeXt), ViT variants (ViT, DeiT, Swin), detection heads, and FPN/BiFPN/PANet necks. Read when choosing or tuning architectures.
- **[references/object_detection_optimization.md](references/object_detection_optimization.md)** — NMS variants, anchor optimization, loss design (focal, GIoU/CIoU/DIoU), training strategies, and detection augmentation. Read when improving detection accuracy.
- **[references/production_vision_systems.md](references/production_vision_systems.md)** — ONNX/TensorRT export, batch inference, edge deployment (Jetson, Intel NCS), Triton serving, and video pipelines. Read when deploying to production.

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

## Anti-Patterns

### Benchmarking Without the Runtime
**Mistake:** Reporting latency or speedup numbers from `inference_optimizer.py` when torch or onnxruntime is not installed.
**Why it happens:** The recommendations print either way, so the run looks complete.
**Instead:** Treat exit 2 from `--benchmark` as "no measurement". Install the runtime, benchmark on the target hardware, and quote only measured numbers.

### Quantizing Without an Accuracy Check
**Mistake:** Shipping an INT8 model because it is 2-4x faster, without re-measuring mAP.
**Why it happens:** Speed is visible immediately; accuracy loss shows up later, on rare classes first.
**Instead:** Re-run validation on the held-out split after every precision change and accept the model only inside the agreed mAP budget.

### Splitting After Augmenting
**Mistake:** Augmenting the whole dataset, then splitting into train/val/test.
**Why it happens:** It feels like one pipeline step.
**Instead:** Split first (stratified), keep val/test untouched, and apply augmentation online during training. Otherwise near-duplicates leak into evaluation and inflate mAP.

## Files

| File | Purpose |
|------|---------|
| `scripts/vision_model_trainer.py` | Dataset analysis and training-config generation |
| `scripts/inference_optimizer.py` | Model analysis, benchmark and optimisation recommendations |
| `scripts/dataset_pipeline_builder.py` | Dataset analyze / convert / split / augment-config / validate |
| `assets/sample_coco_valid/annotations.json` | Sound COCO sample (validate exits 0) |
| `assets/sample_coco_flawed/annotations.json` | Flawed COCO sample (validate exits 1) |
| `references/*.md` | Workflows, command catalogs, architectures, optimisation and deployment detail |
