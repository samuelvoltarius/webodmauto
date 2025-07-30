@echo off
echo Erstelle fehlende Vue-Komponenten...

mkdir src\layouts 2>nul
mkdir src\views\auth 2>nul
mkdir src\views\admin 2>nul
mkdir src\views\reseller 2>nul
mkdir src\views\user 2>nul
mkdir src\views\errors 2>nul
mkdir src\views\viewer 2>nul
mkdir src\components 2>nul

echo ^<template^>^<div^>ResellerLayout^</div^>^</template^>^<script^>export default { name: 'ResellerLayout' }^</script^> > src\layouts\ResellerLayout.vue

echo ^<template^>^<div^>Unauthorized^</div^>^</template^>^<script^>export default { name: 'Unauthorized' }^</script^> > src\views\auth\Unauthorized.vue

echo ^<template^>^<div^>Admin Dashboard^</div^>^</template^>^<script^>export default { name: 'AdminDashboard' }^</script^> > src\views\admin\Dashboard.vue
echo ^<template^>^<div^>Admin Resellers^</div^>^</template^>^<script^>export default { name: 'AdminResellers' }^</script^> > src\views\admin\Resellers.vue
echo ^<template^>^<div^>Admin Users^</div^>^</template^>^<script^>export default { name: 'AdminUsers' }^</script^> > src\views\admin\Users.vue
echo ^<template^>^<div^>Admin Backups^</div^>^</template^>^<script^>export default { name: 'AdminBackups' }^</script^> > src\views\admin\Backups.vue
echo ^<template^>^<div^>Admin System Logs^</div^>^</template^>^<script^>export default { name: 'AdminSystemLogs' }^</script^> > src\views\admin\SystemLogs.vue

echo ^<template^>^<div^>Reseller Dashboard^</div^>^</template^>^<script^>export default { name: 'ResellerDashboard' }^</script^> > src\views\reseller\Dashboard.vue
echo ^<template^>^<div^>Reseller Users^</div^>^</template^>^<script^>export default { name: 'ResellerUsers' }^</script^> > src\views\reseller\Users.vue
echo ^<template^>^<div^>Reseller User Detail^</div^>^</template^>^<script^>export default { name: 'ResellerUserDetail' }^</script^> > src\views\reseller\UserDetail.vue
echo ^<template^>^<div^>Reseller Branding^</div^>^</template^>^<script^>export default { name: 'ResellerBranding' }^</script^> > src\views\reseller\Branding.vue
echo ^<template^>^<div^>Reseller Settings^</div^>^</template^>^<script^>export default { name: 'ResellerSettings' }^</script^> > src\views\reseller\Settings.vue
echo ^<template^>^<div^>Reseller Backup^</div^>^</template^>^<script^>export default { name: 'ResellerBackup' }^</script^> > src\views\reseller\Backup.vue

echo ^<template^>^<div^>User Dashboard^</div^>^</template^>^<script^>export default { name: 'UserDashboard' }^</script^> > src\views\user\Dashboard.vue
echo ^<template^>^<div^>User Projects^</div^>^</template^>^<script^>export default { name: 'UserProjects' }^</script^> > src\views\user\Projects.vue
echo ^<template^>^<div^>User Project Detail^</div^>^</template^>^<script^>export default { name: 'UserProjectDetail' }^</script^> > src\views\user\ProjectDetail.vue
echo ^<template^>^<div^>User Project Upload^</div^>^</template^>^<script^>export default { name: 'UserProjectUpload' }^</script^> > src\views\user\ProjectUpload.vue
echo ^<template^>^<div^>User Profile^</div^>^</template^>^<script^>export default { name: 'UserProfile' }^</script^> > src\views\user\Profile.vue

echo ^<template^>^<div^>Not Found^</div^>^</template^>^<script^>export default { name: 'NotFound' }^</script^> > src\views\errors\NotFound.vue
echo ^<template^>^<div^>Server Error^</div^>^</template^>^<script^>export default { name: 'ServerError' }^</script^> > src\views\errors\ServerError.vue

echo ^<template^>^<div^>Project Viewer^</div^>^</template^>^<script^>export default { name: 'ProjectViewer' }^</script^> > src\views\viewer\ProjectViewer.vue

echo Alle fehlenden Komponenten erstellt!