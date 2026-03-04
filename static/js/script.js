document.addEventListener('DOMContentLoaded', function(){
	const toggle = document.querySelector('.nav-toggle');
	const nav = document.querySelector('nav');
	if(toggle && nav){
		toggle.addEventListener('click', function(){
			nav.classList.toggle('nav-open');
		});
	}
});
