py.test --cov polibeepsync polibeepsync
pyflakes polibeepsync/*.py
pyflakes polibeepsync/tests/*.py
flake8 polibeepsync/*.py
flake8 polibeepsync/tests/*.py
coverage html
xdg-open htmlcov/index.html
