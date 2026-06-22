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
  updated: 2026-06-17
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

Before generating training configs or pipelines, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Task** — detection / instance or semantic segmentation / classification (selects the architecture and `--task`)
- [ ] **Dataset** — location and format (COCO / YOLO / VOC) to analyze or convert (the input to `dataset_pipeline_builder.py`)
- [ ] **Deployment target** — GPU / edge / mobile (drives architecture choice and `inference_optimizer --target`)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `vision_model_trainer.py` | Generate training configs for YOLO / Detectron2 / MMDetection | `python scripts/vision_model_trainer.py data/coco/ --task detection --arch yolov8m -o configs/train.yaml` |
| `inference_optimizer.py` | Analyze, benchmark, and recommend optimizations for a model | `python scripts/inference_optimizer.py model.pt --analyze --benchmark --recommend --target edge` |
| `dataset_pipeline_builder.py` | Analyze/convert/split/augment/validate CV datasets (subcommands) | `python scripts/dataset_pipeline_builder.py analyze --input data/coco/` |

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

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `senior-ml-engineer` | Model serving and MLOps pipeline setup | Trained model artifacts (.pt, .onnx) flow into `model_deployment_pipeline.py` for containerized serving and monitoring |
| `senior-data-engineer` | Dataset ETL and storage pipelines | Raw image data ingested via `pipeline_orchestrator.py`; cleaned datasets flow into `dataset_pipeline_builder.py` for CV formatting |
| `senior-data-scientist` | Experiment design and statistical analysis | Experiment parameters from `experiment_designer.py` guide hyperparameter search; model metrics feed back for significance testing |
| `senior-devops` | CI/CD and GPU infrastructure provisioning | Optimized model artifacts deployed via CI/CD pipelines; GPU node scaling managed through infrastructure-as-code |
| `senior-prompt-engineer` | Multimodal RAG and vision-language integration | Vision model embeddings and detections feed into `rag_system_builder.py` for multimodal retrieval pipelines |
| `senior-cloud-architect` | Cloud GPU resource planning and cost optimization | Benchmark results from `inference_optimizer.py` inform instance type selection and auto-scaling policies |
