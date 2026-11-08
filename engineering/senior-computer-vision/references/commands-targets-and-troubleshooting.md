# Common Commands, Performance Targets, Anti-Patterns, Troubleshooting & Success Criteria

Read this for framework command catalogs (YOLO, Detectron2, MMDetection, optimization), performance targets, anti-patterns to avoid, the troubleshooting table, and the success-criteria bar.

## Common Commands

### Ultralytics YOLO

```bash
# Training
yolo detect train data=coco.yaml model=yolo26m.pt epochs=100 imgsz=640

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
trtexec --onnx=model.onnx --saveEngine=model.engine --fp16 --memPoolSize=workspace:4096M

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

## Anti-Patterns

- **Training without data audit** -- skipping `dataset_pipeline_builder.py analyze` leads to corrupted images, duplicate pairs, and class imbalance surprises mid-training
- **Deploying FP32 to production** -- always export to FP16 minimum; FP32 wastes 2x memory and 1.5-2x latency for <0.5% mAP difference
- **Ignoring calibration dataset** -- INT8 quantization with random samples causes 5-10% mAP drop; use 500+ representative images from the training distribution
- **One-size-fits-all architecture** -- using YOLOv8x for edge deployment or YOLOv8n for high-accuracy requirements; match architecture to deployment target
- **Benchmarking without warmup** -- first N inference calls include JIT compilation overhead; always use `--warmup 10` for accurate measurements
- **Skipping ONNX validation** -- export can silently produce incorrect models; always run `onnx.checker.check_model()` after export

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
