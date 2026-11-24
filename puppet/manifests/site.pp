# Time Manager deployment with Puppet (declarative, idempotent)
$project_dir = $facts['project_dir'] ? {
  undef   => '/project',
  default => $facts['project_dir'],
}
$image     = 'timemanager:puppet'
$container = 'timemanager-puppet'
$port      = '5052'

Exec { path => ['/usr/local/bin', '/usr/bin', '/bin'], provider => shell }

exec { 'build-image':
  command => "docker build -t ${image} ${project_dir}",
  unless  => "docker image inspect ${image} >/dev/null 2>&1",
  timeout => 600,
}

exec { 'create-volume':
  command => 'docker volume create timemanager_puppet_data',
  unless  => 'docker volume inspect timemanager_puppet_data >/dev/null 2>&1',
}

exec { 'run-container':
  command => "docker rm -f ${container} 2>/dev/null; docker run -d --name ${container} -p ${port}:5000 -v timemanager_puppet_data:/data --restart unless-stopped ${image}",
  unless  => "docker ps --filter name=^${container}\$ --filter status=running -q | grep -q .",
  require => [Exec['build-image'], Exec['create-volume']],
}

notify { "Time Manager managed by Puppet -> http://localhost:${port}":
  require => Exec['run-container'],
}
