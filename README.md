# 🖼️ I Hate Background API

Uma API REST poderosa para remoção automática de fundos de imagens usando inteligência artificial.

## ✨ Características

- 🤖 **Remoção automática de fundo** com IA de última geração (BiRefNet-matting)
- 📁 **Múltiplos formatos** suportados: WEBP, PNG, JPG, JPEG
- ⚡ **Detecção automática de GPU** (fallback para CPU quando necessário)
- 🚀 **API REST simples e rápida** com FastAPI
- 🎯 **Alta qualidade** com redimensionamento para 1024x1024
- 🔧 **Fácil de usar** com apenas um endpoint
- 🐳 **Suporte ao Docker** para deploy fácil
- 🔒 **CORS habilitado** para uso em aplicações web

## 🛠️ Instalação e Execução

### Pré-requisitos

- **Python 3.10+**
- **CUDA** (opcional, para aceleração GPU)
- **Git** (para clone do repositório)

### 🚀 Configuração Rápida

1. **Clone e acesse o diretório:**
```bash
git clone https://github.com/lusrodri/canva-copy-api.git
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
```

4. **Execute a API:**
```bash
fastapi run main.py
```

A API estará disponível em: `http://localhost:8000`

### 🐳 Executando com Docker

1. **Build da imagem:**
```bash
docker build -t canva-copy-api .
```

2. **Execute o container:**
```bash
docker run -p 8000:8000 canva-copy-api
```

### 🤖 Modelo de IA

- **Modelo:** `ZhengPeng7/BiRefNet-matting` (carregado automaticamente do Hugging Face)
- **Qualidade:** Estado da arte em remoção de fundos com matting refinado
- **Tamanho:** ~600MB (download automático na primeira execução)
- **Tecnologia:** BiRefNet com suporte a matting para bordas mais suaves

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

O `BackgroundRemover` utiliza o modelo **BiRefNet-matting** e segue este fluxo:

1. **📥 Pré-processamento:**
   - Redimensionamento para 1024x1024 pixels
   - Normalização com valores ImageNet
   - Conversão para tensor PyTorch

2. **🧠 Predição:**
   - Processamento com modelo de segmentação BiRefNet
   - Aplicação de função sigmoid na saída
   - Detecção automática de dispositivo (GPU/CPU)

3. **📤 Pós-processamento:**
   - Conversão da máscara para PIL Image
   - Redimensionamento da máscara para tamanho original
   - Aplicação como canal alpha (transparência)
   - Preservação da qualidade e dimensões originais

4. **🎯 Otimizações:**
   - Precisão float32 otimizada
   - Cache do modelo carregado
   - Processamento em lote eficiente
   - Matting refinado para bordas mais suaves

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
**✅ Solução:** O modelo BiRefNet não requer autenticação. Verifique se o modelo está sendo baixado corretamente.

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

**❌ Erro de modelo não encontrado:**
```
OSError: ZhengPeng7/BiRefNet-matting does not appear to be a repository
```
**✅ Solução:** Verifique sua conexão com a internet. O modelo será baixado automaticamente na primeira execução.

## 📋 Requisitos do Sistema

- **RAM:** Mínimo 4GB, recomendado 8GB+
- **Espaço:** ~2GB livres (modelo + dependências)
- **GPU:** Opcional (NVIDIA com CUDA 11.8+)
- **Rede:** Conexão para download inicial do modelo
- **Python:** Versão 3.10 ou superior

## 🛠️ Stack Tecnológica

- **FastAPI** - Framework web moderno e rápido
- **PyTorch** - Deep learning framework
- **Transformers** - Biblioteca Hugging Face para modelos
- **Pillow** - Processamento de imagens
- **BiRefNet** - Modelo estado da arte para remoção de fundo
- **Docker** - Containerização para deploy

## 🚀 Deploy

### Variáveis de Ambiente

O projeto não requer variáveis de ambiente específicas, mas você pode configurar:

```bash
# Opcional: forçar uso de CPU
export CUDA_VISIBLE_DEVICES=""

# Opcional: definir cache do Hugging Face
export HF_HOME=/path/to/cache
```

### Deploy com Docker

```bash
# Build
docker build -t canva-copy-api .

# Run em produção
docker run -d -p 8000:8000 --name bg-remover canva-copy-api
```

## 🧪 Testes

Execute os testes unitários:

```bash
python test_bg_remover.py
```

## 📊 Performance

- **Tempo médio:** 2-5 segundos por imagem (dependendo do hardware)
- **GPU recomendada:** RTX 3060 ou superior
- **CPU fallback:** Funcional, porém mais lento (10-30 segundos)
- **Tamanho máximo recomendado:** 4096x4096 pixels

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🙏 Agradecimentos

- [ZhengPeng7/BiRefNet](https://github.com/ZhengPeng7/BiRefNet) - Modelo de segmentação de alta qualidade
- [Hugging Face](https://huggingface.co/) - Plataforma de modelos e transformers
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno para Python

## 📞 Suporte

Se você encontrar algum problema ou tiver sugestões:

1. Verifique se o problema já foi reportado nas [Issues](https://github.com/lusrodri/canva-copy-api/issues)
2. Se não, crie uma nova issue com detalhes do problema
3. Para dúvidas gerais, use as [Discussions](https://github.com/lusrodri/canva-copy-api/discussions)

---

**⭐ Se este projeto foi útil para você, considere dar uma estrela no repositório!**