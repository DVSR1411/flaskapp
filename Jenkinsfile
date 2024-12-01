pipeline {
    agent any
    tools {
        dockerTool "docker"
        git "Default"
    }
    stages {
        stage('Git Clone') {
            steps {
                git 'https://github.com/DVSR1411/flaskapp.git'
            }
        }
        stage('Docker Build') {
            steps {
                withCredentials([string(credentialsId: 'docker', variable: 'demo')]) {
                    sh "docker login -u dvsr1411 -p $demo"
                    sh "docker build -t dvsr1411/flaskapp:v$env.BUILD_NUMBER ."
                    sh "docker push dvsr1411/flaskapp:v$env.BUILD_NUMBER" 
                }
            }
        }
        stage('Update manifest') {
            steps {
                build job: 'updatemanifest', parameters: [string(name: 'dockertag', value: "v$env.BUILD_NUMBER")]
            }
        }
    }
}