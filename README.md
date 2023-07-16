# udptransfer

Implementação de protocolo confiável sobre o protocolo não confiável UDP.

## Instruções

É necessário ter o Python (3.x) instalado para execução. Em seguida, basta executar:

```
$ python3 server.py
```

para iniciar o servidor. Para iniciar a conexão, é necessário criar um arquivo na raíz do projeto com o nome `file.test`, e eviá-lo para o servidor executando `python3 client.py`. Isso irá gerar um relatório com todos os logs do tráfego.