document.addEventListener('DOMContentLoaded', function(){
  const tabs = document.querySelectorAll('.role');
  const roleInput = document.getElementById('id_role');

  if(!tabs.length) return;

  tabs.forEach(tab=>{
    tab.addEventListener('click', ()=>{
      tabs.forEach(t=>t.classList.remove('active'));
      tab.classList.add('active');
      const role = tab.dataset.role || 'cliente';
      if(roleInput) roleInput.value = role;
    });
  });
});
