# Define the paths
$djangoPath = "E:\_wip\ous_agile_devops_ai\oad_ai"
$frontendPath = "E:\_wip\ous_agile_devops_ai\oad_ai\oad_ai_frontend"

# Define the ports
$ports = @(8001, 3001)

# Define the time limit
$timeLimit = 7050 # ~2 hours
$startTime = Get-Date
$endTime = $startTime.AddSeconds($timeLimit)

# Function to check if a port is in use and get the process ID
function Test-Port {
    param (
        [int]$port
    )
    $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connection) {
        return $connection.OwningProcess
    } else {
        return $null
    }
}

# Function to stop a process by port
function Stop-ProcessByPort {
    param (
        [int]$port
    )
    $processId = Test-Port -port $port
    if ($processId) {
        Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    }
}

# Function to start Django and frontend services
function Start-Services {
    # Stop Django server if running
    Stop-ProcessByPort -port 8001
    # Start Django server
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c E: && cd $djangoPath && .venv\Scripts\activate && cd $djangoPath && python manage.py runserver 0.0.0.0:8001 --noreload" -NoNewWindow

    # Print Django server status
    $hostname = [System.Net.Dns]::GetHostName()
    $localIP = [System.Net.Dns]::GetHostByName($hostname).AddressList[0].ToString()
    Start-Sleep -Seconds 5 # Give some time for the server to start
    if (Test-Port -port 8001) {
        Write-Host "Django server started successfully!"
        Write-Host "Django can be viewed in the browser at the below URLs:"
        Write-Host "  Local:            http://127.0.0.1:8001"
        Write-Host "  On Your Network:  http://$localIP:8001"
    } else {
        Write-Host "Failed to start the Django server."
    }

    # Stop frontend service if running
    Stop-ProcessByPort -port 3001
    # Start frontend service
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c E: && cd $frontendPath && npm run build && npm start" -NoNewWindow

    # Print React frontend status
    Start-Sleep -Seconds 5 # Give some time for the server to start
    if (Test-Port -port 3001) {
        Write-Host "React frontend started successfully!"
        Write-Host "Frontend can be viewed in the browser at the below URLs:"
        Write-Host "  Local:            http://127.0.0.1:3001"
        Write-Host "  On Your Network:  http://$localIP:3001"
    } else {
        Write-Host "Failed to start the React frontend."
    }
}

# Start services initially
Start-Services

# Main loop to check if services are up every 5 minutes
while ((Get-Date) -lt $endTime) {
    Start-Sleep -Seconds 300
    Start-Services
}

Write-Host "Timeout of $timeLimit seconds reached. Terminating job."

# Clean up processes if necessary
Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "node" -Force -ErrorAction SilentlyContinue
