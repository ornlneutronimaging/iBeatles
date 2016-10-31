from setuptools import setup, find_packages
import os
import sys
import versioneer  # https://github.com/warner/python-versioneer

if sys.argv[-1] == 'pyuic':
    indir = 'designer'
    outdir = 'ibeatles/interfaces'
    files = os.listdir(indir)
    files = [os.path.join('designer', item) for item in files]
    files = [item for item in files if item.endswith('.ui')]

    done = 0
    for inname in files:
        outname = inname.replace('.ui', '.py')
        outname = outname.replace(indir, outdir)
        if os.path.exists(outname):
            if os.stat(inname).st_mtime < os.stat(outname).st_mtime:
                continue
        print("Converting '%s' to '%s'" % (inname, outname))
        command = "pyuic4 %s -o %s"  % (inname, outname)
        os.system(command)
        done += 1
    if not done:
        print("Did not convert any '.ui' files")
    sys.exit(0)

if sys.argv[-1] == 'pyrcc4':
    infile = 'ibeatles/icons/icon.qrc'
    outfile = 'ibeatles/interfaces/icons_rc.py'
    print("Converting icons_rc file")
    command = "pyrcc4 -o %s %s" % (outfile, infile)
    os.system(command)

setup(name="iBeatles",
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description = "Bragg Edge Fitting and Strain Calculator",
      author = "Jean",
      author_email = "j35@ornl.gov",
      url = "http://github.com/ornlneutronimaging/iBeatles",
      long_description = """Should have a longer description""",
      license = "The MIT License (MIT)",
      scripts=["scripts/ibeatles"],
      packages=find_packages(),
      package_dir={},
      install_requires=['numpy','matplotlib'],
      setup_requires=[],
)
