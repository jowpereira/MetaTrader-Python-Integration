# Projeto de Integração MetaTrader e Python

Este projeto explora a ideia de construir um sistema que permita testar um modelo Python diretamente no Strategy Tester do MetaTrader. Essa abordagem acrescenta uma camada adicional de flexibilidade à criação de modelos, aproveitando a simplicidade do Python. O processo de validação ocorre no próprio MetaTrader, já que o modelo é exportado em formato ONNX para o MQL5. Isso significa que você pode moldar e aprimorar seu modelo com facilidade, enquanto a validação rigorosa acontece no ambiente MetaTrader, garantindo que ele esteja pronto para enfrentar as complexidades do mercado financeiro.

## Estrutura de Pastas e Arquivos

- **Demo.ex5** e **Demo.mq5**: Estes arquivos representam o programa principal do MQL5, que será compilado e executado no MetaTrader.

- **Libraries/**
  - FileCSV.mqh
  - Monitor.mqh
  - WorkSymbol.mqh

- **python/**
  - **Model/**
    - __init__.py
    - **model_train/**
      - modelo.pkl
    - model_train.py
    - util.py
  - **Services/**
    - __init__.py
    - file.py
  - __main__.py


## Pré-Requisitos

Antes de iniciar este projeto, certifique-se de que o seguinte esteja configurado em sua máquina:

- [Python](https://www.python.org/) instalado na mesma máquina onde o MetaTrader 5 está configurado (por exemplo, em um ambiente Windows).
- As bibliotecas necessárias estão instaladas. Você pode instalá-las executando o seguinte comando no terminal:

```
pip install -r requirements.txt
```

## Executando o Projeto

Para executar o projeto, siga estas etapas:

1. Abra um terminal ou prompt de comando.

2. Navegue até a pasta do projeto onde você possui o arquivo `__main__.py`.

3. Certifique-se de que o MetaTrader 5 esteja em execução.

4. Execute o seguinte comando para iniciar o projeto:

```
python __main__.py
```

5. Inicie o Testador de Estratégia no MetaTrader 5 para testar o modelo Python diretamente no ambiente MetaTrader.

Certifique-se de consultar o arquivo [README.md](./README.md) para obter informações adicionais e detalhadas sobre como usar este projeto de forma eficaz.

Essas adições explicam os pré-requisitos necessários para usar o projeto, como instalar as bibliotecas de requisitos e como executar o projeto, incluindo a integração com o MetaTrader 5. Espero que isso ajude! Se precisar de mais informações ou ajustes, por favor, me informe.
