import subprocess
import webbrowser
import shutil

from pathlib import Path


def _rm_recursive(path: Path, pattern: str):
    """
    Glob the given relative pattern in the directory represented by this path,
        calling shutil.rmtree on them all
    """

    for p in path.glob(pattern):
        shutil.rmtree(p, ignore_errors=True)


def clean_build():
    """
    Cleans the build
    """

    shutil.rmtree(Path("build"), ignore_errors=True)
    shutil.rmtree(Path("dist"), ignore_errors=True)
    shutil.rmtree(Path(".eggs"), ignore_errors=True)

    _rm_recursive(Path("."), "**/*.egg-info")
    _rm_recursive(Path("."), "**/*.egg")


def clean_coverage():
    """
    Cleans the coverage results
    """

    Path(".coverage").unlink(missing_ok=True)

    for path in Path(".").glob(".coverage.*"):
        path.unlink(missing_ok=True)

    shutil.rmtree(Path("htmlcov"), ignore_errors=True)


def clean_docs():

    for path in Path("docs/api").glob("*.rst"):
        path.unlink(missing_ok=True)

    subprocess.run(["make", "clean"], cwd=Path("docs"), shell=True)


def clean_pyc():
    """
    Cleans compiled files
    """

    _rm_recursive(Path("."), "**/*.pyc")
    _rm_recursive(Path("."), "**/*.pyo")
    _rm_recursive(Path("."), "**/*~")
    _rm_recursive(Path("."), "**/__pycache__")


def clean_test():
    """
    Cleans the test store
    """

    shutil.rmtree(Path(".pytest_cache"), ignore_errors=True)


def coverage():
    """
    Runs the unit test coverage analysis
    """

    subprocess.run(["coverage", "run", "--source", "pyreal", "-m", "pytest"])
    subprocess.run(["coverage", "report", "-m"])
    subprocess.run(["coverage", "html"])

    url = Path("htmlcov/index.html").absolute()
    webbrowser.open(url)


def docs():
    """
    Cleans the doc builds and builds the docs
    """

    clean_docs()

    subprocess.run(["make", "html"], cwd=Path("docs"), shell=True)


def fix_lint():
    """
    Fixes all linting and import sort errors. Skips init.py files for import sorts
    """

    subprocess.run(["autoflake", "--in-place", "--recursive",
                   "--remove-all-unused-imports", "--remove-unused-variables", "pyreal"])
    subprocess.run(["autoflake", "--in-place", "--recursive",
                   "--remove-all-unused-imports", "--remove-unused-variables", "tests"])
    subprocess.run(["autopep8", "--in-place", "--recursive", "--aggressive", "pyreal", "tests"])
    subprocess.run(["isort", "--atomic", "pyreal", "tests", "--skip", "__init__.py"])


def lint():
    """
    Runs the linting and import sort process on all library files and tests and prints errors.
        Skips init.py files for import sorts
    """
    subprocess.run(["flake8", "pyreal", "tests"])
    subprocess.run(["isort", "-c", "pyreal", "tests", "--skip", "__init__.py"])


def test():
    """
    Runs all test commands.
    """

    test_unit()
    test_readme()
    test_tutorials()


def test_readme():
    """
    Runs all scripts in the README and checks for exceptions
    """

    test_path = Path('tests/readme_test')
    shutil.rmtree(test_path, ignore_errors=True)

    test_path.mkdir(parents=True, exist_ok=True)
    shutil.copy('README.md', test_path / 'README.md')

    subprocess.run(["rundoc", "run", "--single-session", "python3",
                   "-t", "python3", "README.md"], cwd=test_path)
    shutil.rmtree(test_path)


def test_tutorials():
    """
    Runs all scripts in the tutorials directory and checks for exceptions
    """

    for ipynb_file in Path("tutorials").glob('**/*.ipynb'):
        checkpoints = ipynb_file.parents[0] / '.ipynb_checkpoints'
        if not checkpoints.is_file():
            subprocess.run(["jupyter", "nbconvert", "--execute",
                            "--ExecutePreprocessor.timeout=60",
                            "--to=html", "--stdout", f"{ipynb_file}"], stdout=subprocess.DEVNULL)


def test_unit():
    """
    Runs all unit tests and outputs results and coverage
    """
    subprocess.run(["pytest", "--cov=pyreal"])


def view_docs():
    """
    Opens the docs in a browser window
    """

    docs()

    url = Path("docs/_build/html/index.html").absolute()
    webbrowser.open(url)
