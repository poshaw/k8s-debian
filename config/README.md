Apply YAML configs to K8S cluster
=================================

# Apply all .yaml files in the directory
$ kubectl apply -f config/

## Make sure .yaml file are included in the correct order
.yaml files will be read in the same order provided by `ls -1`
$ ls -1
01-first-yaml.yaml
02-second-yaml.yaml
...

## Only .yaml files are process in this way
ie this README will be ignored by the above command
