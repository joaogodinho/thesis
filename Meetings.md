# Meetings

## 17Jul2017

### To do

* Identify the __pioneers__, ie, vendors that are among the first nth (to determine) to mark a program as malware and this is then verified by more than mth other vendors.
* create the multi-graph witht the dependencies among names (only do this for the pioneers)
* colocar os dados numa BD (fica mais rápido?)
* contactar virustotal para ver se é possvel criar um classificador usando info dos dados deles, e depois eventualmente criar um serviço que usa esse classificador.
* ver se o wannacry e o petya teriam esbarrado no nosso classificador.

## 27Jul2017

* Graphics with the entry-classifications for malware. How many vendors classify as malware on 1st submission. This needs to be restricted only to those we consider to be malware at the end.
* Proportion of changes that are correct (from non-malware to malware, and it is, and from malware to non-malware, when it is not) and incorrect (in the same graphic)
* Considerar apenas os vendors que classificam mais de 90%. Ou normalizar cada antivirus pelo número de amostras que ele disse qq coisa? Ie, não penalizar por ele não existir no sistema ao início. Ou encontrar o ponto no tempo em que cada vendor começou a classificar tempo `t0` e normalizar cada vendor pelo número total de amostras `n0` submetidas desde o período `t0`. Podemos calcular se há grande difetença entre `n0` e o número de amostras classificadas pelo vendor desde o tempo `t0`.

### Euro Security and Privacy: due August 15, 2017
  * Early reject notification	September 25, 2017
  * Rebuttal period	Oct 27-Nov 3, 2017
  * Notification	November 20, 2017

### Security and Privacy: due November 4, 2017
Até agora temos
* Classificador que usa info estática (dll). Ver se as Detections Rates são boas, e os FP baixos. Comparar com o que existe.
* Dados sobre os nomes. Conseguimos agregar os nomes? Conseguimos arranjar mapas entre nomes usados pelos vendors.
* Identificação dos pioneiros?

## 19Feb2018

* Preparar analise dinamica para a próxima reunião: vector apenas com as calls a cada funçao. ver se dá melhores resultados que o estatico. quão melhores
* Introduzir os conceitos teoricos, concept drift, etc.
* fazer contas para ver pq 3 folds de treino são suficientes, em vez de 2 ou 4.
