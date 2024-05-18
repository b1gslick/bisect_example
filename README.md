# Repo for play with git bisect

## run project

```sh
poetry shell
```

```sh
poetry install
```

```sh
fastapi dev main.py
```

## sh example for auto bisect run

put it into any where
provide 2 path

```bash
export path_to_sh=/path/where/your/store/sh
```

```bash
export path_to_this_repo=/path/where/your/store/this/repo
```

```bash
#!/bin/bash
# test.sh

if git merge --no-commit --no-ff test; then
  $path_to_sh/check_test_case.sh
  status=$?
else
  status=125
fi

rm -rf $path_to_this_repo/bisect_example/__pycache__
git reset --hard
exit $status
```

```bash
#!/bin/sh
# check_test_case.sh

pytest $path_to_this_repo/bisect_example -k "test_change_offer_recalculate_price_from_old_price"
```
