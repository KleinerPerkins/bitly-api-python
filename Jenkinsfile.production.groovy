#!groovy
import groovy.json.JsonSlurperClassic
import groovy.json.JsonOutput

pipeline {
    agent any
    environment {
        BUILD_NUMBER = "${env.BUILD_NUMBER}"
        RUN_ARTIFACT_DIR = "tests/${BUILD_NUMBER}"

        toolbelt = "${env.PYTHON_PATH}"

        SLACK_CHANNEL_EMAIL = "n6r8i1n2g9a6m1u0@kp.slack.com"

        PYPISERVER = "aws-pypiserver"
        PACKAGE_NAME = "bitly_api"

        winscp = "c:\\Program Files (x86)\\WinSCP\\winscp.exe"

        PYPISERVER_ALIAS = "kppypi"

    }
    stages {
        stage('checkout source') {
            steps {
                // when running in multi-branch job, one must issue this command
                checkout scm
            }
        }


        stage('Update package version') {
            steps {
                script {
                    rc = bat(returnStatus: true, script: "dir")
                }
            }
        }

        stage('Create package') {
            steps {
                script {
                    rc = bat(returnStatus: true, script: "${toolbelt} setup.py sdist")
                }
            }
        }

        stage('Publish KP pypiserver') {
            steps {
                script {
                    echo 'Publishing package to kp-pypiserver'
                    rc = bat(returnStatus: true, script: "${toolbelt} setup.py sdist upload -r ${PYPISERVER_ALIAS}")
                    if(rc != 0) { error 'Failure uploading package to kp-pypiserver' }
                }
            }
        }

        stage('Send Completion Email') {
            steps {
                emailext (
                        to: "allen@kleinerperkins.com",
                        replyTo: "allen@kleinerperkins.com",
                        subject: "Deployed ${PACKAGE_NAME} package to KP pypiserver",
                        body: "Package Deploy Completed"
                )
            }
        }
    }
}