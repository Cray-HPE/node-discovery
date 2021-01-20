@Library('dst-shared@master') _

dockerBuildPipeline {
 app = "node-discovery"
 name = "cms-node-discovery"
 description = "Cray management system node discovery agent"
 repository = "cray"
 imagePrefix = "cray"
        product = "csm"
 githubPushRepo = "Cray-HPE/node-discovery"
 githubPushBranches = /(release\/.*|master)/
}
