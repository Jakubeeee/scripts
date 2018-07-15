# This script removes external tool generated files and directories from project leaving source files only
# Removes eclipse, intellij, maven and other generated files
import os
import shutil

projectLocation = os.path.dirname(os.path.realpath(__file__))
# projectLocation = 'path/to/project'

FILES_TO_DELETE = ['.project', '.classpath', 'maven-eclipse.xml', '.iml']
DIRS_TO_DELETE = ['target', 'bin', 'out', '.settings', '.externalToolBuilders', '.metadata', '.recommenders',
                  'RemoteSystemsTempFiles', 'Servers', '.mvn', '.idea', '.sonarlint']


def delete_files(parent, files_names, files_to_delete):
    for file_name in files_names:
        if file_name in files_to_delete:
            file_path = os.path.join(parent, file_name)
            delete_file(file_path)


def delete_file(file_path):
    os.remove(file_path)
    print('Removed file: ' + file_path)


def delete_dirs(parent, dir_names, dirs_to_delete):
    for dir_name in dir_names:
        if dir_name in dirs_to_delete:
            dir_path = os.path.join(parent, dir_name)
            delete_dir(dir_path)


def delete_dir(dir_path):
    shutil.rmtree(dir_path, ignore_errors=True)
    print('Removed directory: ' + dir_path)


for parent, dir_names, files_names in os.walk(projectLocation):
    delete_files(parent, files_names, FILES_TO_DELETE)
    delete_dirs(parent, dir_names, DIRS_TO_DELETE)
