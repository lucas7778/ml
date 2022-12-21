pipeline {
    agent any
    
    environment {
    	APP_SUBFOLDER = 'FPSO_Energy_Analytics\\FPSO_Solucao\\Front_end\\FPSO_Interface'
    }
    
    stages {
        stage('Clean-up') {
            steps {
                bat 'del %APP_SUBFOLDER%\\fpso_interface.spec'
                bat 'del %APP_SUBFOLDER%\\fpso_interface.zip'
                bat 'rmdir /s /q %APP_SUBFOLDER%\\__pycache__'
                bat 'rmdir /s /q %APP_SUBFOLDER%\\build'
                bat 'rmdir /s /q %APP_SUBFOLDER%\\dist'
            }
        }
        
        stage('Build') {
            steps {
                bat 'python %APP_SUBFOLDER%\\build.py %APP_SUBFOLDER%'
            }
        }
        
        stage('Deliver') {
            steps {
                zip zipFile: env.APP_SUBFOLDER + '\\fpso_interface.zip', archive: false, dir: env.APP_SUBFOLDER + '\\dist\\fpso_interface'
            }
            post {
                success {
                    archiveArtifacts env.APP_SUBFOLDER + '\\fpso_interface.zip'
                }
            }
        }
    }
}
