#! /usr/bin/python
# coding=utf-8
# import pysvn
from __future__ import print_function, division, with_statement
from os.path import isfile, join
import glob
import os
import pickle
import subprocess
import sys
import shutil
from datetime import date
from optparse import OptionParser
from subprocess import Popen, PIPE
from xml.dom import minidom


class Bob(OptionParser, object):
    def __init__(self):
        """
        @brief: Initializes a new .
        @param: None
        @raise: None
        """
        self.dft_val()
        count = len(sys.argv) - 1
        if count <= 16:
            if count == 2:
                self.set_val(sys.argv[1], sys.argv[2])
            elif count > 2:
                i = 1
                val = count / 2
                for x in range(int(val)):
                    self.set_val(sys.argv[i], sys.argv[i + 1])
                    i = i + 2
        else:
            print("To Many Arguments")
            exit()
        self.pt_val()

        super(Bob, self).__init__()
        self.usage = "usage: %prog {\
                    \n\t{-b|--build-script} <Path(relative to checkout-path)for the build-script used to build the source code> | \
                    \n\t{-l|--pre-build}    <Pre-build script to sanitize the code before build> | \
                    \n\t{-v|--version}      <Specify version  no. to be set for the build> | \
                    \n\t{-p|--patch}        Specify if code needs to updated by applying patches | \
                    \n\t{-d|--apply-dir}    <PATCH   | Patch dir to from where to pick patched from> | \
                    \n\t{-e|--revert-dir}   <PATCH   | Patch dir to from where to pick patched from> | \
                    \n\t{-c|--patch-cmd}    <PATCH   | Specify command to be used to apply patches Default: \"patch -p0\" | \
                    \n\t{-f|--patch-prefix} <PATCH   | If Specified patch files with patch-prefix would be choosen> | \
                    \n\t{-s|--svn}          Specify if code is available in SVN | \
                    \n\t{-n|--svn-repo}     <SVN     | Path to the build-script used to build the source code> | \
                    \n\t{-r|--svn-revision} <SVN     | Choose this option to try build a specific revision> | \
                    \n\t{-k|--checkout-path}<SVN     | Specify the path of Checkout location> | \
                    \n\t{-z|--release}      Specify if code needs to be added to Tag directory  | \
                    \n\t{-x|--binaries}     <RELEASE | Binaries location, specify comma seperated> | \
                    \n\t{-t|--tag-dir}      <RELEASE | tag directory to place the binaries and source code> | \
                    \n\t{-a|--svn-base-rev} <RELEASE | SVN base revision to start picking Release notes info from> | \
                    \n\t{-u|--upload}       Specify this option if you want to upload the binaries, source and release notes to SFTP | \
                    \n\t{-y|--sftp-path}    <UPLOAD  | SFTP path to upload to Path to the build-script used to build the source code>}"
        self.__cmdArgs = {}
        (optionArgsMap, args) = self.__parseArguments()
        self.__cmdArgs["build-script"] = optionArgsMap.buildScript
        self.__cmdArgs["pre-build"] = optionArgsMap.preBuild
        self.__cmdArgs["version"] = optionArgsMap.version
        self.__cmdArgs["patch"] = optionArgsMap.patch
        self.__cmdArgs["apply-dir"] = optionArgsMap.patchApplyDir
        self.__cmdArgs["revert-dir"] = optionArgsMap.patchRevertDir
        self.__cmdArgs["patch-cmd"] = optionArgsMap.patchCmd
        self.__cmdArgs["patch-prefix"] = optionArgsMap.patchPrefix
        self.__cmdArgs["svn"] = optionArgsMap.svn
        self.__cmdArgs["svn-repo"] = optionArgsMap.svnRepo
        self.__cmdArgs["svn-revision"] = optionArgsMap.svnRevision
        self.__cmdArgs["checkout-path"] = optionArgsMap.svnCheckoutPath
        self.__cmdArgs["release"] = optionArgsMap.release
        self.__cmdArgs["binaries"] = optionArgsMap.releaseBinaries
        self.__cmdArgs["tag-dir"] = optionArgsMap.releaseTagDir
        self.__cmdArgs["svn-base-rev"] = optionArgsMap.releaseSvnBaseRev
        self.__cmdArgs["upload"] = optionArgsMap.upload
        self.__cmdArgs["sftp-path"] = optionArgsMap.uploadSFTPPath

        # starting the execution at the time of object creation by calling this execute() method.
        self.execute()

    def error(self, msg=None):
        """
        @brief: OptionParser error() method overriden 
        - Raised in case of any error while parsing or validating user input.
        - It will print Option parser usage and will exit.
        @param msg: (String) Error message to be printed on terminal.
        @return: None
        @raise: None
        """
        print("%s" % self.usage)
        if msg:
            print("***Error: %s" % msg)
        else:
            print("Please enter the command again as per above command format")
        sys.exit(1)

    def __parseArguments(self):
        """
        @brief: Add options for parsing user input.
        Validates user input after parsing.
        @param: None
        @return: None
        @raise: None
        """
        self.add_option(
            "-b",
            "--build-script",
            dest="buildScript",
            type="string",
            action="callback",
            callback=self.__isOptionValueSet,
            help="<Path(relative to checkout-path)for the build-script used to build the source code>"
        )
        self.add_option(
            "-l",
            "--pre-build",
            dest="preBuild",
            type="string",
            action="callback",
            callback=self.__isOptionValueSet,
            help="<Pre-build script to sanitize the code before build>"
        )
        self.add_option(
            "-v",
            "--version",
            dest="version",
            type="string",
            action="callback",
            callback=self.__isOptionValueSet,
            help="<Specify version  no. to be set for the build>"
        )
        self.add_option(
            "-p",
            "--patch",
            dest="patch",
            action="store_true",
            default=False,
            help="Specify if code needs to updated by applying patches"
        )
        self.add_option(
            "-d",
            "--apply-dir",
            dest="patchApplyDir",
            type="string",
            action="callback",
            callback=self.__isOptionValueSet,
            help="<PATCH   | Patch dir to from where to pick patched from>"
        )
        self.add_option(
            "-e",
            "--revert-dir",
            dest="patchRevertDir",
            type="string",
            action="callback",
            callback=self.__isOptionValueSet,
            help="<PATCH   | Patch dir to from where to pick patched from>"
        )
        self.add_option(
            "-c",
            "--patch-cmd",
            dest="patchCmd",
            type="string",
            action="callback",
            callback=self.__isOptionValueSet,
            help="<PATCH   | Specify command to be used to apply patches Default: \"patch -p0\""
        )
        self.add_option(
            "-f",
            "--patch-prefix",
            dest="patchPrefix",
            type="string",
            action="callback",
            callback=self.__isOptionValueSet,
            help="<PATCH   | If Specified patch files with patch-prefix would be chosen>"
        )
        self.add_option(
            "-s",
            "--svn",
            dest="svn",
            action="store_true",
            default=False,
            help="Specify if code is available in SVN"
        )
        self.add_option(
            "-n",
            "--svn-repo",
            dest="svnRepo",
            type="string",
            action="callback",
            callback=self.__isOptionValueSet,
            help="<SVN     | Path to the build-script used to build the source code>"
        )
        self.add_option(
            "-r",
            "--svn-revision",
            dest="svnRevision",
            type="string",
            action="callback",
            callback=self.__isOptionValueSet,
            help="<SVN     | Choose this option to try build a specific revision>"
        )
        self.add_option(
            "-k",
            "--checkout-path",
            dest="svnCheckoutPath",
            type="string",
            action="callback",
            callback=self.__isOptionValueSet,
            help="<SVN     | Specify the path of Checkout location>"
        )
        self.add_option(
            "-z",
            "--release",
            dest="release",
            action="store_true",
            default=False,
            help="Specify if code needs to be added to Tag directory"
        )
        self.add_option(
            "-x",
            "--binaries",
            dest="releaseBinaries",
            type="string",
            action="callback",
            callback=self.__isOptionValueSet,
            help="<RELEASE | tag directory to place the binaries and source code>"
        )
        self.add_option(
            "-t",
            "--tag-dir",
            dest="releaseTagDir",
            type="string",
            action="callback",
            callback=self.__isOptionValueSet,
            help="<RELEASE | tag directory to place the binaries and source code>"
        )
        self.add_option(
            "-a",
            "--svn-base-rev",
            dest="releaseSvnBaseRev",
            type="string",
            action="callback",
            callback=self.__isOptionValueSet,
            help="<RELEASE | SVN base revision to start picking Release notes info from>"
        )
        self.add_option(
            "-u",
            "--upload",
            dest="upload",
            action="store_true",
            default=False,
            help="Specify this option if you want to upload the binaries, source and release notes to SFTP"
        )
        self.add_option(
            "-y",
            "--sftp-path",
            dest="uploadSFTPPath",
            type="string",
            action="callback",
            callback=self.__isOptionValueSet,
            help="<UPLOAD  | SFTP path to upload to Path to the build-script used to build the source code>"
        )
        self.add_option(
            "-m",
            "--mail",
            dest="mail-address",
            type="string",
            action="callback",
            callback=self.__isOptionValueSet,
            help="<MAIL  | Set whether to send mail to user or not, set mail addresses of users>"
        )

        (optionArgsMap, args) = self.parse_args()
        print(args)
        return (optionArgsMap, args)

    def __isOptionValueSet(self, option, opt, value, parser):
        """
        @brief: Ensures that option is specified only once on command line
        @param option: (Instance) Option instance that.s calling the callback
        @param opt: (String) option string on the command-line that.s triggering the callback
        @param value: (String) argument to this option on the command-line
        @param parser: (Instance) OptionParser instance
        @return: None 
        @raise: None
        """
        if parser.values.ensure_value(option.dest, None):
            self.error()
            # logError("Option %s is already specified" % option)
        setattr(parser.values, option.dest, value)

    def __validateUserInput(self):
        """
        @brief: Validates user input.
        @param args: (List) list of extra arguments passed on command-line
        @return: None
        @raise: None
        """
        self.__validateFilePath()

    def __validateFilePath(self):
        """
        @brief: Validates file-path
        @param : None
        @return: None
        @raise: None
        """
        print("god-svn-repo: %s" % self.__cmdArgs["godSvnRepo"])
        print("minigod-svn-repo: %s" % self.__cmdArgs["miniGodSvnRepo"])
        if not os.path.isdir(self.__cmdArgs["godSvnRepo"]):
            self.error("Directory does not exist against option: <%s> "
                       % "g | god-svn-repo")
        if not os.listdir(self.__cmdArgs["godSvnRepo"]):
            self.error("Directory is empty against option: <%s> "
                       % "g | god-svn-repo")
        if not os.path.isdir(self.__cmdArgs["miniGodSvnRepo"]):
            self.error("Directory does not exist against option: <%s> "
                       % "m | mini-god-svn-repo")
        if not os.listdir(self.__cmdArgs["godSvnRepo"]):
            self.error("Directory is empty against option: <%s> "
                       % "m | mini-god-svn-repo")

    def __hasManualChanges(self, svnDir):
        """
        @brief: Checks if svnDir has some unchecked manual changes.
        @param : None
        @return: 'True' if changes are there
        @raise: None
        """
        commandResult = os.popen("svn diff " + svnDir)
        diffResult = commandResult.read(10)
        commandResult.close()
        return diffResult != ''

    def __svnCheckOut(self):
        """
        @brief: Checks if svnDir has some unchecked manual changes.
        @param : None
        @return: 'True' if changes are there
        @raise: None
        """
        if os.path.exists(self.svn_path+'/trunk'):
            shutil.rmtree(self.svn_path+'/trunk')
        string = 'cd {0};svn co http://shadow.inet.nec.co.jp/svn/NCC_LTU/trunk  --username {1} --password {1} --non-interactive'.format(self.svn_path, 'harmanpreet.kaur')
        exit_code = subprocess.call(string, shell=True)
        if exit_code==1:
            print('ERROR doing checkout! EXITING!!')
            sys.exit(1)

    def __svnCopy(self):
        """
        @brief: Checks if svnDir has some unchecked manual changes.
        @param : None
        @return: 'True' if changes are there
        @raise: None
        """
        today = date.today().strftime("%Y%m%d")
        cmd = 'cd {0};svn copy http://shadow.inet.nec.co.jp/svn/NCC_LTU/trunk http://shadow.inet.nec.co.jp/svn/NCC_LTU/tags/{1}_STEP3_POWER_CTC_LTU_trunk_Version_V{2}_0{3}_{4} -m "Tag for build V{2}-0{3}-${4}_{1}" --username {5} --password {5} --non-interactive'.format(self.checkout_path,today, self.version_major, self.version_minor, self.version_internal, 'harmanpreet.kaur')
        exit_code = subprocess.call(cmd, shell=True)
        if exit_code==1:
            print('error making revision tag. EXITING!!!!')

    def __editVersionTxt(self):
        filePath = self.checkout_path + '/build_utils/LTU4DP2-version.txt'
        if os.path.exists(filePath):
            with open(filePath, 'r+') as f:
                fileTxt = '''. APP.sh
    LTU-8XP2 {0}.0{1}-{2}
    APP svn+ssh://147.76.76.162/var/lib/svn ng/branches/3.0/APP 23198
    iss svn+ssh://147.76.76.162/var/lib/svn ng/branches/3.0/ISS 23198
    sdk svn+ssh://147.76.76.162/var/lib/svn ng/branches/3.0/SDK 23198
    kernel svn+ssh://147.76.209.106/var/lib/svn branches/8e1000/3.0/kernel_space 5012
    '''.format(self.version_major, self.version_minor,
               self.version_internal)
                f.seek(0)
                f.write(fileTxt)
                f.truncate()
        else:
            print('couldn\'t find {0}. EXITING!!!'.format(filePath))
            sys.exit(1)
        exit_code = subprocess.call('cd {0};svn commit -m "updated version.txt for build ver: {1}-0{2}-{3}" --username {4} --password {4} --non-interactive'.format(self.checkout_path, self.version_major, self.version_minor, self.version_internal, 'harmanpreet.kaur'), shell=True)
        if exit_code==1:
            print('failing to commit. EXITING!')
            sys.exit(1)
        elif exit_code==0:
            print('Successfully commited!')

    def __changeCOREIPM(self):
        if os.path.exists(self.checkout_path + "/APP/ltu4dp2/COREIPM_8XP_020803.image"):
            cmd = "cd " + self.checkout_path + "/APP/ltu4dp2/;cp COREIPM_8XP_020803.image COREIPM_LTU_4DP2_LATEST.image"
            print("running " + cmd)
            exit_code = subprocess.call(cmd, shell=True)
            if exit_code==1:
                print('copy COREIPM operation failed. EXITING!')
                sys.exit(1)
            else:
                print('sucessfully copied COREIPM image files')
        else:
            print('Couldn\'t locate COREIPM image file in APP/ltu4dp2/')
            sys.exit(1)

    def __build(self):
        """
        @brief: Execute predefined script
        @param: build script
        @Return : none
        @raise: None
        """
        autoboot_from = self.svn_path+'/AutoBoot_Script_V02_POWER_afterNonAuto.sh'
        if not os.path.exists(autoboot_from):
            print('{0} is not there. Please check existence or name!'.format(autoboot_from))
            sys.exit(1)
        exit_code = subprocess.call('cp -p {0} {1}'.format(autoboot_from, self.checkout_path), shell=True)
        if exit_code==1:
            print('error copying AutoBoot script to build directory. EXITING')
            sys.exit(1)
        print("build script execution start")
        exit_code =subprocess.call('cd {0};./AutoBoot_Script_V02_POWER_afterNonAuto.sh'.format(self.checkout_path), shell=True)
        if exit_code==1:
            print("Build operation was unsuccessful.EXITING!!!")
            sys.exit(1)

    def __isSuccess(self):
        mib_release_patharray = glob.glob(self.three_path + '/Power_MIB*.zip')[0].split('/')
        mib_release = mib_release_patharray[len(mib_release_patharray) - 1]
        paths = [self.checkout_path+'/pkgBinaries/'+self.bin_name, self.checkout_path+'/iss/code/future/LR/ISS.exe',
                 self.checkout_path+'/iss/code/future/LR/ISS.exe.map', self.three_path + '/App2300_R333_1.129604.tkf',
                 self.three_path + '/README', self.three_path+'/{0}'.format(mib_release)
                 ]
        for path in paths:
            if os.path.exists(path):
                pass
            else:
                print('ERROR!!! {0} can\'t be acessed with path - {1}. EXITING!!!!'.format(path.split('/')[-1], path))
                sys.exit(1)


    def __copyOperation(self):
        mib_release_patharray = glob.glob(self.three_path + '/Power_MIB*.zip')[0].split('/')
        mib_release = mib_release_patharray[len(mib_release_patharray) - 1]
        dirPath = self.copy_container
        print("dir path where files are being copied is :" + dirPath)
        if os.path.exists(dirPath):
            shutil.rmtree(dirPath)
        os.mkdir(dirPath)
        exit_code = subprocess.call(
            "cp {0}/pkgBinaries/{1} {2};cp {0}/iss/code/future/LR/ISS.exe {2};cp {0}/iss/code/future/LR/ISS.exe.map {2};cp {3}/{4} {2}".format(
                self.checkout_path,self.bin_name,dirPath,self.three_path,mib_release
            ), shell=True)
        if exit_code == 0:
            print("copied bin, iss.exe and iss.exe.map, MIB successfully")
        elif exit_code == 1:
            print("copying operation for bin, iss.exe iss.exe.map and MIB unsuccessful. EXITING!")
            sys.exit(1)
        self.__copyPONFW(dirPath)

    def __copyPONFW(self, dirPath):
        filePathOne = self.three_path + '/App2300_R333_1.129604.tkf'
        filePathTwo = self.three_path + '/README'
        cmd = 'cp {0} {2}; cp {1} {2}'.format(filePathOne, filePathTwo, dirPath)

        exit_code = subprocess.call(cmd, shell=True)
        if exit_code == 0:
            print("copied PONFW file successfully.")
        else:
            print("copying operation for PONFW file unsuccessful. EXITING!")
            sys.exit(1)

    def __computingCksum(self, path):
        proc = Popen('cksum {0}'.format(path), shell=True, stdin=PIPE,
                     stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()
        if out:
            out_arr = out.split(' ')
            temp = out_arr[2].split('/')
            third = temp[len(temp) - 1]
            return out_arr[0] + ' ' + out_arr[1] + ' ' + third
        else:
            return 'ERROR Calculating cksum'

    def __computingCRC(self):
        proc = Popen(
            'cd {0}/pkgBinaries;./am31hdr -l {1}'.format(self.checkout_path, self.bin_name), shell=True,
            stdin=PIPE, stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()
        if out:
            out_arr = out.split('\n')
            return out_arr[0] + '\n' + out_arr[2]
        else:
            return 'ERROR fetching CRC'

    def __releaseFILETAG(self):
        proc = Popen('cd {0};svn info'.format(self.checkout_path), shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()
        # perform operation on out to extract relevent info given in README file
        if out:
            out_arr = out.split('\n')
            return out_arr[1] + '\n' + out_arr[4]
        else:
            return 'ERROR fetching File tag'

    def __makeBCM(self):
        apptkf = 'App2300_R333_1.129604.tkf'
        exit_code = subprocess.call(
            'cd {0};cat {1} {2} > LTU-8XP2_V{3}_0{4}_{5}-BCM55538R333.bin'.format(self.copy_container,
                                                                                 self.bin_name, apptkf,
                                                                                 self.version_major,
                                                                                 self.version_minor,
                                                                                 self.version_internal
                                                                                 ),
            shell=True
        )
        if exit_code == 0:
            print('LTU-8XP2_V{0}_0{1}_{2}-BCM55538R333.bin made successfully.'.format(self.version_major,
                                                                                     self.version_minor,
                                                                                     self.version_internal))
        else:
            print('Error making LTU-8XP2_V{0}_0{1}_{2}-BCM55538R333.bin. EXITING!'.format(self.version_major,
                                                                                self.version_minor,
                                                                                self.version_internal))
            sys.exit(1)

    def __createPackage(self):
        dirPath = self.copy_container
        files = [f for f in os.listdir(dirPath) if isfile(join(dirPath, f))]
        files = sorted(files)
        if len(files)<7:
            print('Any of the required files is missing to make package. EXITING!!')
            sys.exit(1)
        else:
            exit_code = subprocess.call('cd {0};tar -czvf {1}.tgz {2} {3} {4} {5} {6} {7}'.format(dirPath, self.package_name, files[1], files[2], files[3], files[4], files[5], files[6]), shell=True)
            if exit_code == 0:
                print('making package operation completed successfully')
                self.__copyPackage()
            else:
                print('making package operation didn\'t complete successfully. EXITING!!')
                sys.exit(1)

    def __copyPackage(self):
        # To be implemented later
        print('####################### Copying the package to shadow server ############################')
        exit_code = subprocess.call('cd {0};scp LTU-8XP2_V{1}_0{2}_{3}.tgz nitinch@10.43.201.50:/mnt/concat/proj/2.5GEPON-OLT/FTP-SPACE/misc/'.format(self.copy_container, self.version_major, self.version_minor, self.version_internal), shell=True)
        if exit_code==1:
            print('ERROR Copying LTU-8XP2_V{0}_0{1}_{2}.tgz!!!!! Please check if shadow server has our ssh key.'.format(self.version_major, self.version_minor, self.version_internal))


    def __sendMAIL(self):
        # will be executed after getting permissions to sent the mail
        # subprocess.call('python sendMail.py', shell=True)
        print('Mail permission yet to be obtained!!')

    def __hasFilesInScope(self, repoType, svnDir):
        """
        @brief: Checks if svnDir has some unchecked manual changes.
        @param : None
        @return: 'True' if changes are there
        @raise: None
        """
        statusList = []
        # If repoType is miniSVN the svn diff should contains files
        # listed in file 'files_in_scope.txt'
        commandResult = os.popen("svn status " + svnDir + " | grep -v ?")
        statusList = commandResult.readlines()
        commandResult.close()
        print("Printing svn status file list:")
        for item in statusList:
            print(item)

    def __executeCloc(self, source, target):
        """
        @brief: Validates file-path
        @param : None
        @return: None
        @raise: None
        """
        for item in self.__filesInScope:
            print("Cloc diff for file: %s" % item[3:])
            commandResult = os.popen("cloc --diff " + source + item[2:] + " " + target + item[2:])
            clocOutput = commandResult.readlines()
            commandResult.close()
            print("Printing output from Cloc:")
            for item2 in clocOutput:
                itemnew = ' '.join(item2.split())
                if itemnew.startswith("SUM:"):
                    break
                if itemnew.startswith("same"):
                    self.__same = self.__same + int(itemnew.split(' ')[-1])
                    print("same: %s" % (itemnew.split(' ')[-1]))
                if itemnew.startswith("modified"):
                    self.__modified = self.__modified + int(itemnew.split(' ')[-1])
                    print("modified: %s" % (itemnew.split(' ')[-1]))
                if itemnew.startswith("added"):
                    self.__added = self.__added + int(itemnew.split(' ')[-1])
                    print("added: %s" % (itemnew.split(' ')[-1]))
                if itemnew.startswith("removed"):
                    self.__removed = self.__removed + int(itemnew.split(' ')[-1])
                    print("removed: %s" % (itemnew.split(' ')[-1]))
            print("-------------------")
        print("Sum of all the cnaged made by NTIL")
        print("swarn same: %s" % self.__same)
        print("swarn modified: %s" % self.__modified)
        print("swarn added: %s" % self.__added)
        print("swarn removed: %s" % self.__removed)

    def execute(self):
        """
        @brief: Executes all the Build Script steps
        @param: None
        @return: None
        @raise: None
        """
        print('#################### Checking out ################################################')
        self.__svnCheckOut()

        print('############################# Editing the version.txt ################################')
        self.__editVersionTxt()

        print('############################ Running "cp COREIPM_8XP_020803.image COREIPM_LTU_4DP2_LATEST.image" ##########')
        self.__changeCOREIPM()

        print("############################ Starting build ##########################")
        self.__build()

        self.__isSuccess()

        print('############################### Running svn copy #####################################')
        self.__svnCopy()

        print('############################### Copying Bin,ISS files,PONFW file,ReadME,BCM bin to a different directory ###############################')
        self.__copyOperation()

        print('############################### Making BCM bin ###############################')
        self.__makeBCM()

        print('############################### Editing the Read me file ###############################')
        self.__editReadme()

        print('############################### Creating the package and copying it ###############################')
        self.__createPackage()

        print('############################### Sending the mail ###############################')
        self.__sendMAIL()

        print('--------------------------------------------------------------')
        print('                      EXECUTION FINISHED                      ')
        print('--------------------------------------------------------------')

    def dft_val(self):
        xmldoc = minidom.parse("args.xml")
        itemlist = xmldoc.getElementsByTagName("item")
        self.svn_repo = itemlist[0].attributes["svn_repo"].value
        self.svn_revision = itemlist[1].attributes["svn_revision"].value
        self.checkout_path = itemlist[2].attributes["checkout_path"].value
        self.build_script_path = itemlist[3].attributes["build_script"].value
        self.version_major = itemlist[4].attributes["VERSION_MAJOR"].value
        self.version_minor = itemlist[5].attributes["VERSION_MINOR"].value
        self.version_internal = itemlist[6].attributes["VERSION_INTERNAL"].value
        self.patch_path = itemlist[10].attributes["patchPath"].value
        self.three_path = itemlist[11].attributes["path_for_mib_readme_tkf"].value
        if self.checkout_path.endswith('/'):
            self.checkout_path = self.checkout_path[:-1]
        self.svn_path = self.checkout_path
        self.checkout_path = self.checkout_path+'/trunk/build'
        self.bin_name = 'LTU-8XP2_V{0}_0{1}_{2}.bin'.format(self.version_major, self.version_minor,
                                                           self.version_internal)
        self.package_name = 'LTU-8XP2_V{0}_0{1}_{2}'.format(self.version_major, self.version_minor,
                                                           self.version_internal)
        self.copy_container = self.checkout_path+'/copy_container'

    def set_val(self, ch, value):
        if ch == "-n":
            self.svn_repo = value
        elif ch == "-r":
            self.svn_revision = value
        elif ch == "-k":
            self.checkout_path = value
        elif ch == "-p":
            self.svnCheckoutPath = value
        elif ch == "-d":
            self.patchApplyDir = value
        elif ch == "-e":
            self.patchRevertDir = value
        elif ch == "-l":
            self.pre_build = value
        elif ch == "-b":
            self.build_script_path = value
        else:
            print("Wrong Input!!!")

    def pt_val(self):
        print("svn_repo =", self.svn_repo)
        print("svn_revision =", self.svn_revision)
        print("checkout_path =", self.checkout_path)
        print("build_script =", self.build_script_path)
        print("version_major =", self.version_major)
        print("version_minor =", self.version_minor)
        print("version_internal =", self.version_internal)
        print("patch_path =", self.patch_path)
        print("svn_path =", self.svn_path)

    def __editReadme(self):
        paths = [self.copy_container+ '/README', self.three_path+'/README']
        report = self.generateReport()
        for path in paths:
            with open(path, 'r+') as f:
                f.seek(0)
                f.write(report)
                f.truncate()

    def generateReport(self):
        mib_release_patharray = glob.glob(self.copy_container + '/Power_MIB*.zip')[0].split('/')
        mib_release = mib_release_patharray[len(mib_release_patharray) - 1]
        fw_date = date.today().strftime('%d%B')
        release_version = self.bin_name
        release_date = date.today().strftime('%Y-%m-%d')
        release_file_tag = self.__releaseFILETAG()
        crc = self.__computingCRC()
        checksum = [self.__computingCksum(self.copy_container + '/ISS.exe'),
                    self.__computingCksum(self.copy_container + '/ISS.exe.map'),
                    self.__computingCksum(
                        self.copy_container+ '/LTU-8XP2_V{0}_0{1}_{2}-BCM55538R333.bin'.format(self.version_major,
                                                                                              self.version_minor,
                                                                                              self.version_internal)),
                    self.__computingCksum(self.copy_container + '/' + self.bin_name),
                    self.__computingCksum(self.copy_container+'/'+ mib_release),
                    self.__computingCksum(self.copy_container+ '/README')
                    ]
        pon_firmware = 'LTU-8XP2_V{0}_0{1}_{2}-BCM55538R333.bin'.format(self.version_major, self.version_minor,
                                                                       self.version_internal)

        report = '''We hereby release the LTU 8XP2 system FW Date : {0} for technical evaluation.

[Applicable Model]
   NS2480 LTU 8XP2(CPLD Ver:1.5 onwards)

[Release Ver.]
   {1} (as in /etc/version.txt).

[Release Date]
   {2}

[Release File Tag]
   {3}


[Supported Contents]
This information will be provided in the release notes.

[Limitations]
This information is in the release notes.

[CRC (display by u-boot fwinfo command)]
{4}

[cksum]   [size]
{5}
{6}
{7}
{8}
{9}
{10}


[contents]
  {1}                          : LTU firmware
  {11}                        : LTU + Pon firmware
  ISS.exe.map                        : ISS.exe MAP File
  README.txt                         : This File
  ISS.exe                            : ISS.exe File
  {12}                        : MIB Release
                '''.format(fw_date, release_version, release_date, release_file_tag, crc, checksum[0], checksum[1],
                           checksum[2], checksum[3], checksum[4], checksum[5], pon_firmware, mib_release
                           )
        with open('report.pkl', 'wb') as output:
            pickle.dump(report, output, protocol=2)
        return report


def main():
    try:
        bObj = Bob()
    except Exception as ex:
        print(ex)


if __name__ == "__main__":
    main()
