# 🦺 Sistema de Detecção de EPIs com Visão Computacional

## 📋 Sobre o Projeto

Este projeto consiste em uma aplicação de Visão Computacional capaz de detectar Equipamentos de Proteção Individual (EPIs) em vídeos ou imagens capturados por webcam ou arquivos pré-gravados.

A solução utiliza técnicas de Processamento Digital de Imagens e Inteligência Artificial para identificar automaticamente a presença de EPIs obrigatórios em trabalhadores, auxiliando no monitoramento da conformidade com normas de segurança do trabalho.

O sistema foi desenvolvido utilizando Python, OpenCV, YOLOv8 e Flask.

---

## 🎯 Objetivos

- Detectar automaticamente EPIs em imagens e vídeos.
- Monitorar o uso correto dos equipamentos de segurança.
- Identificar situações de não conformidade.
- Exibir os resultados em uma interface web amigável.
- Gerar métricas de desempenho da solução.

---

## 🛠 Tecnologias Utilizadas

| Tecnologia | Finalidade |
|------------|------------|
| Python | Linguagem principal |
| OpenCV | Processamento de imagens e vídeo |
| YOLOv8 | Detecção de objetos utilizando IA |
| Flask | Interface Web |
| NumPy | Manipulação de dados |
| Pandas | Geração de relatórios |
| HTML/CSS | Interface do usuário |

---

## 🏗 Arquitetura do Sistema

<img width="429" height="765" alt="image" src="https://github.com/user-attachments/assets/425cd6d7-a4a1-4a0c-8560-35c046fb237d" />

---

## 🦺 EPIs Detectados

O sistema pode ser treinado para reconhecer os seguintes equipamentos:

- Capacete de segurança
- Colete refletivo
- Óculos de proteção
- Luvas de proteção
- Máscara de proteção
- Botas de segurança

---

## 🤖 Inteligência Artificial

A detecção é realizada utilizando o modelo YOLOv8.

Classes utilizadas:

| ID | Classe |
|----|---------|
| 0 | Person |
| 1 | Helmet |
| 2 | Goggles |
---

## 🖼 Processamento de Imagem

Além da detecção baseada em IA, são utilizadas técnicas de processamento digital de imagens:

### Conversão para escala de cinza

```python
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
```

### Equalização de Histograma

```python
gray = cv2.equalizeHist(gray)
```

### Filtro Gaussiano

```python
blur = cv2.GaussianBlur(frame, (5,5), 0)
```

### Operações Morfológicas

```python
opening = cv2.morphologyEx(
    mask,
    cv2.MORPH_OPEN,
    kernel
)
```

---

## ⚙ Instalação

### Clonar o repositório

```bash
git clone https://github.com/seu-usuario/epi-detector.git

cd epi-detector
```

### Criar ambiente virtual

Linux:

```bash
python3 -m venv venv

source venv/bin/activate
```

Windows:

```bash
python -m venv venv

venv\Scripts\activate
```

### Instalar dependências

```bash
pip install -r requirements.txt
```

---

## 📦 Dependências

```text
ultralytics
opencv-python
flask
numpy
pandas
```

---

## 🧠 Treinamento do Modelo

Treinamento utilizando YOLOv8:

```bash
yolo detect train \
data=data.yaml \
model=yolov8n.pt \
epochs=50 \
imgsz=640
```

Ao final do treinamento:

```text
runs/detect/train/weights/best.pt
```

Copie o arquivo para:

```text
model/best.pt
```

---

## ▶ Executando o Projeto

Inicie a aplicação:

```bash
python app.py
```

Acesse:

```text
http://localhost:5000
```

---

## 📊 Métricas de Desempenho

O sistema registra indicadores importantes para avaliação:

- FPS (Frames por Segundo)
- Tempo médio de inferência
- Quantidade de detecções
- Quantidade de alertas
- Precisão (Precision)
- Revocação (Recall)
- F1-Score

Exemplo:

| Métrica | Valor |
|----------|---------|
| FPS Médio | 28 |
| Tempo Inferência | 32 ms |
| Precisão | 92% |
| Recall | 89% |
| F1-Score | 90% |

---

## 🚨 Detecção de Não Conformidade

O sistema verifica automaticamente a presença dos EPIs obrigatórios.

Exemplo:

```text
Pessoa 01

✓ Capacete
✓ Colete
✓ Óculos

Status: Conforme
```

```text
Pessoa 02

✗ Capacete
✓ Colete
✗ Óculos

Status: Não Conforme
```

---

## 📈 Funcionalidades Futuras

- Upload de vídeos
- Captura automática de infrações
- Dashboard estatístico
- Rastreamento de pessoas
- Banco de dados para histórico de eventos
- Notificações em tempo real

---

## 🔬 Critérios Atendidos

### Processamento de Imagem

- Conversão para escala de cinza
- Equalização de histograma
- Filtros de suavização
- Operações morfológicas

### Inteligência Artificial

- Detecção de objetos com YOLOv8
- Reconhecimento de múltiplos EPIs

### Interface Gráfica

- Dashboard Web utilizando Flask

### Análise de Desempenho

- FPS
- Tempo de inferência
- Precisão
- Recall
- F1-Score

### Qualidade da Solução

- Arquitetura modular
- Fácil manutenção
- Escalável para novos EPIs

---

## 👨‍💻 Autores

Projeto desenvolvido para fins acadêmicos na disciplina de Visão Computacional.

Alunos: **João Victor Surdi, Vinicius Fantin, Sara Gibmaier**

Instituição: **UNOESC - Campus Videira**

Ano: **2026**
