#*****************************************************************************
#   Copyright 2004-2008 Steve Menard
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#*****************************************************************************

print('-' * 70)
print("The java classes used are defined in the test harness.")
print("The class jpype.rmi.ServerImpl must be started before this script can "
      "be run.")
print('-' * 70)

from jpype import java, startJVM, shutdownJVM, getDefaultJVMPath
import os.path

# Compute paths
root = os.path.abspath(os.path.dirname(__file__))
classes = os.path.abspath(os.path.join(root, '..', 'test', 'classes'))
print(classes)
print(root)
print("-Djava.class.path={0}".format(root))
#startJVM(getDefaultJVMPath(), "-ea", "-Djava.class.path={0}".format(root))
#startJVM(getDefaultJVMPath(), "-ea", "-Djava.ext.dirs={0}".format(root))
startJVM("C:/Program Files/Java/jre7/bin/server/jvm.dll","-ea")

shutdownJVM()