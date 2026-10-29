# Pilot run 报告：Qwen3.5-2B 本地运行（Apple M4）

日期：2026-10-28 · 分支：`local-mps-pilot` · 基于 `main@9a8dce1`

## 1. 设置

| 项目 | 值 |
|---|---|
| 硬件 | MacBook，Apple M4（10 核），24 GB 统一内存，MPS 后端 |
| 软件 | Python 3.11，torch 2.15.0，transformers 5.19.0，zeus 0.16.0 + zeus-apple-silicon 1.1.0 |
| 模型 | `Qwen/Qwen3.5-2B`，bf16，greedy decoding，thinking 关闭 |
| 数据 | `data/preprocessed/combined.csv`，en + sw，每个数据集取前 30 题 → 180 条查询 |
| 命令 | `python data/generate.py --models qwen3.5-2b --languages en sw --items-per-dataset 30 --output results/pilot_m4.jsonl` |
| 用时 | 推理共 48 分钟（不含模型加载），中途无报错、无 OOM |

**能耗口径**：`energy_consumption` 是 M4 片上 GPU 的能耗（J），通过 IOReport 计数器读取，不需要 sudo。这和 RunPod 上 NVML 只算 GPU 的口径一致。但硬件不同，**数值不能和 RunPod 的数据直接比较或合并**；`hardware=Apple M4` 和 `energy_method=apple` 两个字段可以用来区分。用 macmon 交叉验证过：两者的 GPU 功率读数一致（1.76 W 对 1.6–1.9 W）。这台机器上 CPU 和 DRAM 的计数器读数为 0，所以没有计入。

## 2. 结果

| 数据集 | 语言 | n | 准确率 | 平均能耗 (J) | 平均延迟 (s) | 输入 token | 输出 token |
|---|---|---|---|---|---|---|---|
| XNLI | en | 30 | 0.567 | 1.31 | 0.85 | 81 | 3 |
| XNLI | sw | 30 | 0.267 | 1.37 | 0.84 | 97 | 3 |
| Belebele | en | 30 | 0.833 | 1.98 | 0.97 | 181 | 3 |
| Belebele | sw | 30 | 0.367 | 3.19 | 1.56 | 307 | 3 |
| MGSM | en | 30 | 0.700 | 39.42 | 45.31 | 97 | 384 |
| MGSM | sw | 30 | 0.233 | 43.82 | 46.89 | 138 | 416 |
| **合计** | | 180 | **0.494** | 15.18 | 16.07 | | |

- **按语言**：en 0.700，sw 0.289。英语和斯瓦希里语的差距在三个数据集上都很大，router 加入语言特征是有依据的。
- **能耗集中在 MGSM**：MGSM 占全部能耗的 91.4%（总计 2,733 J），XNLI 和 Belebele 每题只要 1–3 J。MGSM 每个输出 token 约 0.10 J（0.085–0.153），所以能耗基本由输出长度决定。
- **sw 的输入更贵**：同一道题，sw 的输入 token 比 en 多 20%–69%（XNLI 多 20%，MGSM 多 42%，Belebele 多 69%），能耗也相应更高。
- **一个零能耗异常**：冒烟测试里有一条 26.6 s 的生成被记成 0.0 J，之后连续三次都没能复现。我已经把测量改成读累计计数器的差值。正式 pilot 中没有出现零能耗的行。

## 3. 发现的问题（RunPod 全量跑之前建议处理）

### 3.1 MGSM 的 512 token 上限不够，被截断的回答会被误判为正确（最重要）
- 60 道 MGSM 里有 21 道写满了 512 token，没有给出 `Answer:`。其中 en 7 道、sw 14 道。
- 被截断的回答没有 `Answer:`，`NumericAnswerExtractor` 就会退回去取全文最后一个数字，于是有 **3 道被误判为正确**（`mgsm_en_0019`、`mgsm_sw_0004`、`mgsm_sw_0019`）。例如 en_0019 截断在 `6/v` 处，取到的 `6` 刚好等于参考答案。
- 去掉这 3 道误判后，MGSM 的准确率是 en 0.667，sw 0.167。
- 没被截断的回答准确率是 en 0.87、sw 0.31；被截断的基本都是错的。
- 建议：(a) 把 MGSM 的 `max_new_tokens` 提高到 1024，或在 prompt 里要求简洁作答；(b) 被截断的输出（没有 `Answer:` 且 `output_tokens == max_new_tokens`）直接判 0 分，或者单独打标记，不要用取最后一个数字的兜底规则。

### 3.2 MGSM 的 stop sequence `####` 几乎不起作用
- prompt 要求按 `Answer: <answer> ####` 的格式作答，但 60 条回答里只有 1 条写了 `####`，模型通常写完 `Answer: 126` 就结束了。
- 目前这不影响准确率，因为模型会自然输出 EOS。但这说明 stop 规则和实际输出格式对不上，同样的情况在大模型上可能会带来多余的生成和能耗。可以考虑把 `Answer:` 后面的那一行也设为停止条件。

### 3.3 sw 的 MGSM 是英文指令加 sw 题目，模型 63% 的时候用英文推理
- 指令 `Solve this step by step...` 不管哪种语言都是英文。按英文关键词粗略统计，sw 题的回答里约 63% 用英文推理，还有翻译和理解上的混乱（例如 sw_0004 把 kuku（鸡）理解成了 boxes）。
- 这是实验设计上的选择：用英文还是题目本身的语言做 CoT。论文里需要写明。

### 3.4 XNLI sw 有严重的选项偏置
- XNLI sw 的 30 道题里有 27 道预测 A（entailment），而参考答案中 A 只有 7 道。0.267 的准确率低于随机水平 0.333，原因是模型几乎每题都回答 A，而不是逐题判断出了错。
- XNLI en 也有一点偏向 A（14 道预测 A，参考答案只有 7 道）。Belebele sw 偏向 C（17 道预测 C，参考 13 道）。
- 对 2B 模型来说这可能就是真实水平。但如果所有模型都在 sw 上退化成同一个选项，XNLI sw 就没法区分模型的好坏了。可以等 9B 和 Gemma 的结果出来再判断。

### 3.5 答案提取的检查
- 多选题：所有输出都是一个干净的字母，抽查没有发现提取错误。
- 数值题：`16.00` 和 `16`、`243.00` 和 `243` 都正确判为相等；没有出现「答案等于参考却判错」的情况。唯一的问题就是 3.1 里截断回答的误判。

## 4. 对后续的意义
- **本地流程已跑通**：数据读取 → 推理 → 答案提取和评分 → 能耗 → JSONL 输出，全部正常，也支持中断后续跑。修改只在新分支上，CUDA 路径保持不变。
- **全量跑在本地不现实**：按这次的速度，2B 模型跑 6,000 题大约需要 26 小时（MGSM 2,000 题 × 约 45 s ≈ 25 小时，其余约 1 小时）。Qwen3.5 的线性注意力层在 Mac 上只能用较慢的参考实现。9B 及以上的模型在 24 GB 内存里也放不下。全量还是要在 RunPod 上跑。
- **本地还能补充跑**：`tiny-aya-global`（约 7 GB，需要 HF 许可）和 `gemma-4-e4b`（约 16 GB）都能放下，可以用同一条命令再做一轮 pilot，比较不同模型在 sw 上的表现。

## 5. 文件位置（仓库根目录 `~/Desktop/carbon-aware_multilingual_router_fork`）

| 文件 | 内容 |
|---|---|
| `results/pilot_m4.jsonl` | 180 行原始结果，每行包括输出、参考答案、准确率、能耗、延迟、token 数 |
| `results/pilot_m4_summary.txt` | `scripts/summarize_pilot.py` 的完整输出，包括错题样例 |
| `results/pilot_m4_report.md` | 本报告 |
| `results/smoke_m4.jsonl` | 6 条冒烟测试结果，其中一行是零能耗异常（`mgsm_en_0001`），只作记录用，不要使用 |
| `logs/pilot_m4.log` | 运行日志 |
| `scripts/summarize_pilot.py` | 统计脚本：`python scripts/summarize_pilot.py results/pilot_m4.jsonl` |
| 代码改动 | `data/generate.py`、`src/services/inference_service.py`、`src/metrics/energy.py`（`git diff main`） |
