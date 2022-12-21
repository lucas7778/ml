import os
import sys
import subprocess

# Instala os pacotes Python necessários
os.system('pip uninstall -y typing')    # remover porque vai apagar o env anterior
os.system('pip install dash')   # colocar todos os installs na mesma linha
os.system('pip install dash_daq')
os.system('pip install dash')
os.system('pip install numpy')
os.system('pip install pandas')
os.system('pip install PyQt5')
os.system('pip install pytz')
os.system('pip install scipy')
os.system('pip install setuptools')
os.system('pip install statsmodels')
os.system('pip install openpyxl')
os.system('pip install sklearn')

# Pega o caminho de instalação dos pacotes para acrescentar o Dash manualmente ao pyinstaller
os.chdir(sys.argv[1])
sproc = subprocess.Popen("pip show dash", shell=True, stdout=subprocess.PIPE)
piptok = sproc.stdout.read().split()
locpos = piptok.index(b'Location:')
pypkgpath = piptok[locpos + 1].decode('utf-8')

# Gera o executável e os arquivos auxiliares
os.system('pyinstaller --add-data "assets\\dashstyle.css;assets" ' +
                      '--add-binary "assets\\petro2.png;assets" ' +
                      '--add-binary "assets\\add.png;assets" ' +
                      '--add-binary "assets\\minus.png;assets" ' +
                      '--add-binary "imgs\\db_icon.png;imgs" ' +
                      '--add-binary "imgs\\ml_icon.png;imgs" ' +
                      '--add-binary "imgs\\imgs.qrc;imgs" ' +
                      '--add-binary "P67_TAGS_SISTEMAS.xlsx;." ' +
                      '--add-data "2022-03-23_Variáveis_Sistemas_P67.csv;." ' +
                      '--add-data "' + pypkgpath + '\\dash\\dcc;dash\\dcc" ' +
                      '--add-data "' + pypkgpath + '\\dash\\html;dash\\html" ' +
                      '--add-data "' + pypkgpath + '\\dash\\dash_table;dash\\dash_table" ' +
                      '--add-data "' + pypkgpath + '\\dash_daq;dash_daq" ' +
                      '--add-data "fpso_interface2.ui;." ' +
                      '--add-data "subsistema_interface.ui;." ' +
                      '--add-data "subsistema_interface2.ui;." ' +
                      '--add-data "fcfi2.ui;." ' +
                      '--add-data "eq.ui;." ' +
                      '--add-binary "eqs.pickle;." ' +
                      '--hidden-import "multiSelCombo2" ' +
                      '--hidden-import="sklearn.utils._typedefs" ' +
                      '--hidden-import="sklearn.utils._heap" ' +
                      '--hidden-import="sklearn.utils.murmurhash" ' +
                      '--hidden-import="sklearn.utils._cython_blas" ' +
                      '--hidden-import="sklearn.utils._fast_dict" ' +
                      '--hidden-import="sklearn.utils._openmp_helpers" ' +
                      '--hidden-import="sklearn.utils._random" ' +
                      '--hidden-import="sklearn.utils._seq_dataset" ' +
                      '--hidden-import="sklearn.utils._sorting" ' +
                      '--hidden-import="sklearn.utils._vector_sentinel" ' +
                      '--hidden-import="sklearn.utils._weight_vector" ' +
                      '--hidden-import="sklearn.neighbors._partition_nodes" ' +
                      '--hidden-import="sklearn.neighbors._quad_tree" ' +
                      '--add-data "' + pypkgpath + '\\dash\\deps;dash\\deps" ' +
                      '--add-data "' + pypkgpath + '\\dash\\dash-renderer;dash\\dash-renderer" ' +
                      'fpso_interface.py')

# Gera a lista de arquivoa para incluir no MSIX
os.chdir('dist\\fpso_interface')
with open('..\\..\\msix\\files_.txt', 'w') as f:
    f.write('[Files]\n')
    f.write('".\\AppxManifest.xml" "AppxManifest.xml"\n')
    f.write('".\\Registry.dat" "Registry.dat"\n')
    f.write('".\\User.dat" "User.dat"\n')
    f.write('".\\UserClasses.dat" "UserClasses.dat"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Square150x150Logo.scale-100.png" "Assets\\FPSOINTERFACE-Square150x150Logo.scale-100.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Square150x150Logo.scale-125.png" "Assets\\FPSOINTERFACE-Square150x150Logo.scale-125.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Square150x150Logo.scale-150.png" "Assets\\FPSOINTERFACE-Square150x150Logo.scale-150.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Square150x150Logo.scale-200.png" "Assets\\FPSOINTERFACE-Square150x150Logo.scale-200.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Square150x150Logo.scale-400.png" "Assets\\FPSOINTERFACE-Square150x150Logo.scale-400.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Square310x310Logo.scale-100.png" "Assets\\FPSOINTERFACE-Square310x310Logo.scale-100.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Square310x310Logo.scale-125.png" "Assets\\FPSOINTERFACE-Square310x310Logo.scale-125.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Square310x310Logo.scale-150.png" "Assets\\FPSOINTERFACE-Square310x310Logo.scale-150.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Square310x310Logo.scale-200.png" "Assets\\FPSOINTERFACE-Square310x310Logo.scale-200.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Square310x310Logo.scale-400.png" "Assets\\FPSOINTERFACE-Square310x310Logo.scale-400.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Square44x44Logo.scale-100.png" "Assets\\FPSOINTERFACE-Square44x44Logo.scale-100.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Square44x44Logo.scale-125.png" "Assets\\FPSOINTERFACE-Square44x44Logo.scale-125.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Square44x44Logo.scale-150.png" "Assets\\FPSOINTERFACE-Square44x44Logo.scale-150.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Square44x44Logo.scale-200.png" "Assets\\FPSOINTERFACE-Square44x44Logo.scale-200.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Square44x44Logo.scale-400.png" "Assets\\FPSOINTERFACE-Square44x44Logo.scale-400.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Square44x44Logo.targetsize-16.png" "Assets\\FPSOINTERFACE-Square44x44Logo.targetsize-16.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Square44x44Logo.targetsize-16_altform-unplated.png" "Assets\\FPSOINTERFACE-Square44x44Logo.targetsize-16_altform-unplated.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Square44x44Logo.targetsize-24.png" "Assets\\FPSOINTERFACE-Square44x44Logo.targetsize-24.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Square44x44Logo.targetsize-24_altform-unplated.png" "Assets\\FPSOINTERFACE-Square44x44Logo.targetsize-24_altform-unplated.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Square44x44Logo.targetsize-256.png" "Assets\\FPSOINTERFACE-Square44x44Logo.targetsize-256.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Square44x44Logo.targetsize-256_altform-unplated.png" "Assets\\FPSOINTERFACE-Square44x44Logo.targetsize-256_altform-unplated.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Square44x44Logo.targetsize-32.png" "Assets\\FPSOINTERFACE-Square44x44Logo.targetsize-32.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Square44x44Logo.targetsize-32_altform-unplated.png" "Assets\\FPSOINTERFACE-Square44x44Logo.targetsize-32_altform-unplated.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Square44x44Logo.targetsize-48.png" "Assets\\FPSOINTERFACE-Square44x44Logo.targetsize-48.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Square44x44Logo.targetsize-48_altform-unplated.png" "Assets\\FPSOINTERFACE-Square44x44Logo.targetsize-48_altform-unplated.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Square71x71Logo.scale-100.png" "Assets\\FPSOINTERFACE-Square71x71Logo.scale-100.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Square71x71Logo.scale-125.png" "Assets\\FPSOINTERFACE-Square71x71Logo.scale-125.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Square71x71Logo.scale-150.png" "Assets\\FPSOINTERFACE-Square71x71Logo.scale-150.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Square71x71Logo.scale-200.png" "Assets\\FPSOINTERFACE-Square71x71Logo.scale-200.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Square71x71Logo.scale-400.png" "Assets\\FPSOINTERFACE-Square71x71Logo.scale-400.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Wide310x150Logo.scale-100.png" "Assets\\FPSOINTERFACE-Wide310x150Logo.scale-100.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Wide310x150Logo.scale-125.png" "Assets\\FPSOINTERFACE-Wide310x150Logo.scale-125.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Wide310x150Logo.scale-150.png" "Assets\\FPSOINTERFACE-Wide310x150Logo.scale-150.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Wide310x150Logo.scale-200.png" "Assets\\FPSOINTERFACE-Wide310x150Logo.scale-200.png"\n')
    f.write('".\\Assets\\FPSOINTERFACE-Wide310x150Logo.scale-400.png" "Assets\\FPSOINTERFACE-Wide310x150Logo.scale-400.png"\n')
    f.write('".\\Assets\\StoreLogo.scale-100.png" "Assets\\StoreLogo.scale-100.png"\n')
    f.write('".\\Assets\\StoreLogo.scale-125.png" "Assets\\StoreLogo.scale-125.png"\n')
    f.write('".\\Assets\\StoreLogo.scale-150.png" "Assets\\StoreLogo.scale-150.png"\n')
    f.write('".\\Assets\\StoreLogo.scale-200.png" "Assets\\StoreLogo.scale-200.png"\n')
    f.write('".\\Assets\\StoreLogo.scale-400.png" "Assets\\StoreLogo.scale-400.png"\n')
    f.write('".\\resources.pri" "Resources.pri"\n')
    for (path, dirs, filenames) in os.walk('.'):
        for fn in filenames:
            if len(path) == 1:
                f.write(
                    '"' + '..\\dist\\fpso_interface\\' + fn + '" "' + fn + '"\n')
            else:
                f.write(
                    '"' + '..\\dist\\fpso_interface\\' + path[2:] + '\\' + fn + '" "' + path[2:] + '\\' + fn + '"\n')

# Gera o MSIX e assina
os.chdir('..\\..')
# os.chdir('msix')
# os.system('makeappx pack /v /o /l /nv /nfv /f files_.txt /p FPSO_interface.msix')
# os.system('signtool sign /fd SHA256 /a FPSO_interface.msix')
