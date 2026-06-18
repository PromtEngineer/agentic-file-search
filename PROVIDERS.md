# LLM Provider Configuration

FsExplorer supports multiple LLM backends through a small provider adapter layer.

## Quick Start

### Google Gemini (default)

```bash
export FS_EXPLORER_LLM_PROVIDER=google
export GOOGLE_API_KEY=your_google_api_key
```

### SiliconFlow (OpenAI-compatible)

```bash
export FS_EXPLORER_LLM_PROVIDER=siliconflow
export SILICONFLOW_API_KEY=your_siliconflow_api_key
# Optional overrides
export FS_EXPLORER_LLM_MODEL=Qwen/Qwen2.5-72B-Instruct
export FS_EXPLORER_LLM_BASE_URL=https://api.siliconflow.cn/v1
# International endpoint: https://api.siliconflow.com/v1
```

Get a SiliconFlow API key at https://cloud.siliconflow.cn/account/ak

### OpenAI

```bash
export FS_EXPLORER_LLM_PROVIDER=openai
export OPENAI_API_KEY=your_openai_api_key
export FS_EXPLORER_LLM_MODEL=gpt-4o-mini
export FS_EXPLORER_LLM_BASE_URL=https://api.openai.com/v1
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `FS_EXPLORER_LLM_PROVIDER` | `google`, `siliconflow`, or `openai` (default: `google`) |
| `FS_EXPLORER_LLM_MODEL` | Model id override |
| `FS_EXPLORER_LLM_BASE_URL` | Base URL for OpenAI-compatible providers |
| `GOOGLE_API_KEY` | Google Gemini API key |
| `SILICONFLOW_API_KEY` | SiliconFlow API key |
| `OPENAI_API_KEY` | OpenAI API key |

## Architecture

```
FsExplorerAgent
    -> llm.create_llm_client()
            -> GoogleGeminiClient      (native JSON schema)
            -> OpenAICompatibleClient  (SiliconFlow, OpenAI, ...)
```

Google Gemini uses native structured JSON output. OpenAI-compatible providers use `response_format=json_object` plus the Action JSON schema embedded in the system prompt, with flexible parsing for imperfect model output.

## Embeddings / Indexing

Vector indexing (`explore index --with-embeddings`) still uses Google Gemini embeddings by default via `GOOGLE_API_KEY`. Chat provider selection is independent of embedding configuration.

## Security

Never commit `.env` or real API keys. Use `.env.example` as a template only.
