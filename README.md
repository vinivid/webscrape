### Web Scraper Imobiliarias de São Carlos

O script transforma as listagen de aluguel das imobiliarias em um csv contendo o valor do aluguel, o tempo andando até a USP e a distância até a USP.

Todos os dados foram coletados das imobilírias https://www.cardinali.com.br e https://roca.com.br.

### Intalação

Na pasta contendo o arquivo "pyproject.toml" use o comando:

```shell
py -m pip install .
```

Sera criado o script 'scrape' no seu ambiente, que é o web scraper.

#### Dependências

Para calcular as distâncias e tempo até a usp utiliza-se da biblioteca osmnx.
Boeing, G. 2024. “Modeling and Analyzing Urban Networks and Amenities with OSMnx.” Working paper. URL: https://geoffboeing.com/publications/osmnx-paper/

Os dados relativos as localização foram adquiridos do open street map https://www.openstreetmap.org/copyright 