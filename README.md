# PhD Paper Experiments

Source code for the experiments backing the papers cited in the doctoral thesis:

> **On the Integration of Business Process Modeling and Constrained Generative AI for Engineering Ecosystem Resilience Prediction Systems**
>
> Tiago Alexandre De Jesus Sousa — Faculty of Science, Technology and Medicine (FSTM), Université du Luxembourg
> Supervisor: Prof. Dr Nicolas Guelfi

Each subdirectory is a self-contained experiment that maps to a paper and to a chapter of the thesis.

## Experiments

| Folder | Thesis chapter | Paper |
|--------|----------------|-------|
| [`cogen/`](./cogen) | Chapter 6 — *COGEN: Constraint-Based Generative AI Agents for Guiding Business Process Instances* | Sousa, Guelfi, Ries. *A Semantically-Grounded Agentic Framework for Assisting BPMN Model Instance Execution*. In *Proceedings of the 14th International Conference on Model-Based Software and Systems Engineering* (MODELSWARD 2026), SCITEPRESS, pages 97–109. [DOI: 10.5220/0014446900004058](https://doi.org/10.5220/0014446900004058). |
| [`dadi/`](./dadi) | Chapter 7 — *DADI: Guiding Data Augmentation with Diffusion-Based Generative AI* | Sousa, Ries, Guelfi. *Data Augmentation in Earth Observation: A Diffusion Model Approach*, Information 16(2):81, MDPI, 2025. [DOI: 10.3390/info16020081](https://doi.org/10.3390/info16020081). |

`cogen/` covers the agentic vs. monolithic LLM pipeline for generating semantically conformant BPMN process code, including the 40 benchmark scenarios, the six-level verification harness, and the per-model result archives reported in the paper.

`dadi/` covers the four-stage pipeline for diffusion-based EO data augmentation: instruction generation, VLM captioning, LoRA fine-tuning of the diffusion backbone, and the downstream CLIP fine-tuning used for evaluation on EuroSAT.

See each folder's own `README.md` for setup, dependencies, and reproduction commands.

## Repository conventions

- Secrets (`.env`, API keys) are never committed — see `.gitignore`. Each experiment that needs credentials documents the required variables in its own README.
- `dadi/diffusers/` is a vendored clone of the [HuggingFace `diffusers`](https://github.com/huggingface/diffusers) repository and is excluded from this repo. Clone it separately if needed.
- Model checkpoints and large binary artifacts are also excluded; reproduction scripts should download or regenerate them.

## How to cite

If you reference these experiments, please cite the corresponding paper.

```bibtex
@inproceedings{sousa2026cogen,
  title     = {A Semantically-Grounded Agentic Framework for Assisting {BPMN} Model Instance Execution},
  author    = {Sousa, Tiago and Guelfi, Nicolas and Ries, Beno{\^i}t},
  booktitle = {Proceedings of the 14th International Conference on Model-Based Software and Systems Engineering (MODELSWARD)},
  pages     = {97--109},
  publisher = {SCITEPRESS},
  year      = {2026},
  isbn      = {978-989-758-798-6},
  issn      = {2184-4348},
  doi       = {10.5220/0014446900004058}
}

@article{sousa2025dadi,
  title     = {Data Augmentation in {Earth Observation}: A Diffusion Model Approach},
  author    = {Sousa, Tiago and Ries, Beno{\^i}t and Guelfi, Nicolas},
  journal   = {Information},
  publisher = {MDPI},
  volume    = {16},
  number    = {2},
  pages     = {81},
  year      = {2025},
  doi       = {10.3390/info16020081}
}
```

The doctoral thesis that frames these experiments is referenced in the thesis manuscript itself; this repository is the artifact backing its experimental appendix.
