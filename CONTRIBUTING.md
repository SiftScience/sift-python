
## Setting up the environment

1. Install [pyenv](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation)
2. Setup virtual environment

```sh
# install necessary Python version
pyenv install 3.13.2 

# create a virtual environment
pyenv virtualenv 3.13.2 v3.13
pyenv activate v3.13
```

3. Upgrade pip

```sh
pip install -U pip
```

4. Install pre-commit

```sh
pip install -U pre-commit
```

5. Install the library:

```sh
pip install -e .
```

## Testing

Before submitting a change, make sure the following commands run without
errors from the root folder of the repository:

```sh
python -m unittest discover
```

## Integration testing app

For testing the app with real calls it is possible to run the integration testing app,
it makes calls to almost all Sift public API endpoints to make sure the library integrates
well. At the moment, the app is run on every merge to master

#### How to run it locally

1. Add env variable `API_KEY` with the valid Api Key associated from the account

```sh
export API_KEY="api_key"
```

1. Add env variable `ACCOUNT_ID` with the valid account id

```sh
export ACCOUNT_ID="account_id"
```

3. Run the following under the project root folder

```sh
# run the app
python test_integration_app/main.py
```
