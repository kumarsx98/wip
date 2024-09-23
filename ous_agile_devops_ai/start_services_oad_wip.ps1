# Define the paths
$djangoPath = "E:\_wip\ous_agile_devops_ai\oad_ai"
$frontendPath = "E:\_wip\ous_agile_devops_ai\oad_ai\oad_ai_frontend"

# Define the ports
$djangoPort = 8001
$frontendPort = 3001

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
        Write-Host "Stopping process with ID $processId on port $port"
        Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    }
}

# Function to start Django and frontend services
function Start-Services {
    # Stop Django server if running
    Stop-ProcessByPort -port $djangoPort

    # Start Django server
    Write-Host "Starting Django server on port $djangoPort"
    Start-Process -NoNewWindow -FilePath "cmd.exe" -ArgumentList "/c E: && cd $djangoPath && .venv\Scripts\activate && cd $djangoPath && python manage.py runserver 0.0.0.0:$djangoPort --noreload" -PassThru | Out-Null

    # Print Django server status
    $hostname = [System.Net.Dns]::GetHostName()
    $localIP = [System.Net.Dns]::GetHostByName($hostname).AddressList[0].ToString()
    Start-Sleep -Seconds 5 # Give some time for the server to start
    if (Test-Port -port $djangoPort) {
        Write-Host "Django server started successfully!"
        Write-Host "Django can be viewed in the browser at the below URLs:"
        Write-Host "  Local:            http://127.0.0.1:$djangoPort"
        Write-Host "  On Your Network:  http://$localIP:$djangoPort"
    } else {
        Write-Host "Failed to start the Django server."
    }

    # Stop frontend service if running
    Stop-ProcessByPort -port $frontendPort

    # Start frontend service
    Write-Host "Starting React frontend on port $frontendPort"
    Start-Process -NoNewWindow -FilePath "cmd.exe" -ArgumentList "/c E: && cd $frontendPath && npm run build && set PORT=$frontendPort && npm start" -PassThru | Out-Null

    # Print React frontend status
    Start-Sleep -Seconds 5 # Give some time for the server to start
    if (Test-Port -port $frontendPort) {
        Write-Host "React frontend started successfully!"
        Write-Host "Frontend can be viewed in the browser at the below URLs:"
        Write-Host "  Local:            http://127.0.0.1:$frontendPort"
        Write-Host "  On Your Network:  http://$localIP:$frontendPort"
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
try {
    Stop-ProcessByPort -port $djangoPort
    Stop-ProcessByPort -port $frontendPort
} catch {
    Write-Warning "Failed to stop some processes: $_"
} finally {
    Write-Host "Processes terminated."
}
