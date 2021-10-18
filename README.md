# medicar

## Aplicação disponível em https://app-medicar.herokuapp.com/

[![Build Status](https://app.travis-ci.com/tarcisio-sousa/medicar.svg?branch=main)](https://app.travis-ci.com/tarcisio-sousa/medicar)
[![Updates](https://pyup.io/repos/github/tarcisio-sousa/medicar/shield.svg)](https://pyup.io/repos/github/tarcisio-sousa/medicar/)
[![Python 3](https://pyup.io/repos/github/tarcisio-sousa/medicar/python-3-shield.svg)](https://pyup.io/repos/github/tarcisio-sousa/medicar/)
[![Codecov](https://codecov.io/gh/tarcisio-sousa/medicar/branch/main/graph/badge.svg?token=J03XMILYTK)](https://codecov.io/gh/tarcisio-sousa/medicar)



## Configuração de Projeto

### Definir as variáveis de ambiente
```
export PIPENV_VENV_IN_PROJECT=1
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
```

### Terminal
**Alias para python manage.py**
```
alias mng='python $VIRTUAL_ENV/../manage.py'
```
```
pip install pipenv
```

```
pipenv sync -d
```

**Copiar arquivo de variáveis de ambiente**
```
cp contrib/env-sample .env
```

**Criar banco de dados `testdb` Postgres 9.5**
```
psql -c "CREATE DATABASE testdb;" -U postgres
```

**Migrar tabelas**
```
python manage.py migrate --noinput
```

**Criar super usuário**
```
python manage.py createsuperuser
```

```
pipenv run flake8 .
pipenv run pytest --cov=core
pipenv run codecov
```
