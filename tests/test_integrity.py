import os

def test_integrity():
    here = os.path.abspath(os.path.dirname(__file__))
    module = os.path.join(here, '..', 'ftis', 'ftis')
    analysers = os.path.join(module, 'analysers')
    common = os.path.join(module, 'common')
    assert os.path.exists(analysers)
    assert os.path.exists(common)
    assert os.path.isdir(analysers)
    assert os.path.isdir(common)

    # Check that all of the analysers have the appropriate files
    # for analyser_folder in os.listdir(analysers):
    #     if analyser_folder not in ['.DS_Store', '__pycache__']:
    #         analyser_contents = os.listdir(
    #             os.path.join(analysers, analyser_folder)
    #             )
    #         analyser_contents.remove('__pycache__')
    #         analyser_contents.remove('.DS_Store')
    #         # try:
    #         #     analyser_contents.remove('__pycache__')
    #         #     analyser_contents.remove('.DS_Store')
    #         # except:
    #         #     pass
    #         print(analyser_contents)
            