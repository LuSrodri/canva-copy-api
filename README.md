# 🖼️ I Hate Background API

Uma API REST poderosa para remoção automática de fundos de imagens usando inteligência artificial.

## ✨ Características

- 🤖 **Remoção automática de fundo** com IA de última geração (RMBG-2.0)
- 📁 **Múltiplos formatos** suportados: WEBP, PNG, JPG, JPEG
- ⚡ **Detecção automática de GPU** (fallback para CPU quando necessário)
- 🚀 **API REST simples e rápida** com FastAPI
- 🎯 **Alta qualidade** com redimensionamento para 1024x1024
- 🔧 **Fácil de usar** com apenas um endpoint

## 🛠️ Instalação e Execução

### Pré-requisitos

- **Python 3.10+**
- **CUDA** (opcional, para aceleração GPU)
- **Token do Hugging Face** ([obter aqui](https://huggingface.co/settings/tokens))

### 🚀 Configuração Rápida

1. **Clone e acesse o diretório:**
```bash
cd canva-copy-api
```

2. **Crie e ative o ambiente virtual:**
```bash
# Criar ambiente virtual
python -m venv env

# Ativar ambiente virtual (Windows)
.\env\Scripts\activate

# Para Linux/Mac
source env/bin/activate
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
pip install -U "huggingface_hub[cli]"
```

4. **Configure o token do Hugging Face:**
```bash
# Opção 1: Login interativo
hf auth login

# Opção 2: Com token direto (substitua YOUR_TOKEN)
hf auth login --token YOUR_TOKEN

# Opção 3: Variável de ambiente (Windows)
set HF_TOKEN=your_token_here
hf auth login --token %HF_TOKEN%
```

5. **Execute a API:**
```bash
fastapi run main.py
```

A API estará disponível em: `http://localhost:8000`

### 🤖 Modelo de IA

- **Modelo:** `briaai/RMBG-2.0` (carregado automaticamente do Hugging Face)
- **Qualidade:** Estado da arte em remoção de fundos
- **Tamanho:** ~1.7GB (download automático na primeira execução)

## 📡 API Endpoints

### `GET /ping`
**Health check** - Verifica se a API está funcionando

**Resposta:**
```json
{
  "status": "ok",
  "message": "I Hate Background API is running"
}
```

### `POST /remove-background`
**Remove o fundo** de uma imagem enviada

**Parâmetros:**
- `file`: Arquivo de imagem (multipart/form-data)
- **Formatos aceitos:** WEBP, PNG, JPG, JPEG
- **Tamanho máximo:** Limitado pela memória disponível

**Resposta:**
- **Sucesso:** Imagem PNG com fundo removido
- **Erro 400:** Arquivo não é uma imagem válida
- **Erro 500:** Erro no processamento

**Exemplo com curl:**
```bash
curl -X POST "http://localhost:8000/remove-background" \
     -H "accept: image/png" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@sua_imagem.jpg" \
     --output resultado.png
```

**Exemplo com Python:**
```python
import requests

url = "http://localhost:8000/remove-background"
files = {"file": open("sua_imagem.jpg", "rb")}

response = requests.post(url, files=files)

if response.status_code == 200:
    with open("resultado.png", "wb") as f:
        f.write(response.content)
    print("Fundo removido com sucesso!")
```

## 🧪 Teste

Para testar a funcionalidade:

```bash
python test_bg_remover.py
```

## ⚙️ Como Funciona?

O `BackgroundRemover` utiliza o modelo **RMBG-2.0** da Bria AI e segue este fluxo:

1. **📥 Pré-processamento:**
   - Redimensionamento para 1024x1024 pixels
   - Normalização com valores ImageNet
   - Conversão para tensor PyTorch

2. **🧠 Predição:**
   - Processamento com modelo de segmentação
   - Aplicação de função sigmoid na saída
   - Detecção automática de dispositivo (GPU/CPU)

3. **📤 Pós-processamento:**
   - Conversão da máscara para PIL Image
   - Aplicação como canal alpha (transparência)
   - Preservação da qualidade original

4. **🎯 Otimizações:**
   - Precisão float32 otimizada
   - Cache do modelo carregado
   - Processamento em lote eficiente

## 🔧 Troubleshooting

### Problemas Comuns

**❌ Erro de CUDA/GPU:**
```
RuntimeError: CUDA out of memory
```
**✅ Solução:** A API automaticamente usa CPU como fallback

**❌ Erro de autenticação HF:**
```
HTTPError: 401 Client Error: Unauthorized
```
**✅ Solução:** Verifique se o token está correto: `hf auth whoami`

**❌ Erro de dependências:**
```
ModuleNotFoundError: No module named 'torch'
```
**✅ Solução:** Reinstale as dependências: `pip install -r requirements.txt`

**❌ Erro de memória:**
```
RuntimeError: [enforce fail at alloc_cpu.cpp]
```
**✅ Solução:** Reduza o tamanho da imagem ou use uma máquina com mais RAM

## 📋 Requisitos do Sistema

- **RAM:** Mínimo 4GB, recomendado 8GB+
- **Espaço:** ~3GB livres (modelo + dependências)
- **GPU:** Opcional (NVIDIA com CUDA 11.8+)
- **Rede:** Conexão para download inicial do modelo

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request