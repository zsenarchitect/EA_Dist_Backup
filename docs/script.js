// Scroll Progress Bar
const scrollProgress = document.createElement('div');
scrollProgress.className = 'scroll-progress';
document.body.appendChild(scrollProgress);

window.addEventListener('scroll', () => {
    const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
    const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const scrolled = (winScroll / height) * 100;
    scrollProgress.style.width = `${scrolled}%`;
});

// Smooth Scroll for Navigation Links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Enhanced Search Functionality
const searchInput = document.getElementById('searchInput');
if (searchInput) {
    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase().trim();
        
        // Search in tool cards
        const toolCards = document.querySelectorAll('.tool-card');
        const sections = document.querySelectorAll('.content-section');
        
        if (searchTerm === '') {
            // Show all sections and tool cards
            sections.forEach(section => {
                section.style.display = 'block';
            });
            toolCards.forEach(card => {
                card.style.display = 'block';
            });
            return;
        }
        
        let hasVisibleCards = {};
        
        // Filter tool cards
        toolCards.forEach(card => {
            const searchData = card.getAttribute('data-search') || '';
            const cardText = card.textContent.toLowerCase();
            const isVisible = searchData.includes(searchTerm) || cardText.includes(searchTerm);
            
            card.style.display = isVisible ? 'block' : 'none';
            
            // Track which sections have visible cards
            const section = card.closest('.content-section');
            if (section && isVisible) {
                const sectionId = section.id;
                hasVisibleCards[sectionId] = true;
            }
        });
        
        // Show/hide sections based on whether they have visible cards
        sections.forEach(section => {
            const sectionId = section.id;
            section.style.display = hasVisibleCards[sectionId] ? 'block' : 'none';
        });
        
        // Update TOC links visibility
        const tocLinks = document.querySelectorAll('.toc .nav-link');
        tocLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && href.startsWith('#')) {
                const sectionId = href.substring(1);
                const listItem = link.closest('li');
                if (listItem) {
                    listItem.style.display = hasVisibleCards[sectionId] ? 'block' : 'none';
                }
            }
        });
    });
    
    // Clear search on Escape key
    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            searchInput.value = '';
            searchInput.dispatchEvent(new Event('input'));
            searchInput.blur();
        }
    });
}

// Intersection Observer for Animations
const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

document.querySelectorAll('.doc-section, .card, .warning-box, .info-box, .tool-card').forEach(el => {
    observer.observe(el);
});

// Mobile Navigation Toggle
const navbarToggler = document.querySelector('.navbar-toggler');
const navbarCollapse = document.querySelector('.navbar-collapse');

if (navbarToggler && navbarCollapse) {
    navbarToggler.addEventListener('click', () => {
        navbarCollapse.classList.toggle('show');
    });

    // Close mobile menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!navbarToggler.contains(e.target) && !navbarCollapse.contains(e.target)) {
            navbarCollapse.classList.remove('show');
        }
    });
}

// Copy Code Blocks
document.querySelectorAll('pre code, .tool-card code').forEach((block) => {
    const button = document.createElement('button');
    button.className = 'btn btn-sm btn-outline-secondary position-absolute';
    button.style.top = '10px';
    button.style.right = '10px';
    button.style.fontSize = '0.75rem';
    button.textContent = 'Copy';
    
    const parent = block.parentNode;
    parent.style.position = 'relative';
    parent.appendChild(button);
    
    button.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        // Extract just the command text for tool cards
        let textToCopy = block.textContent;
        if (block.closest('.tool-card')) {
            textToCopy = textToCopy.replace('Command: ', '');
        }
        
        navigator.clipboard.writeText(textToCopy).then(() => {
            button.textContent = 'Copied!';
            button.classList.add('btn-success');
            button.classList.remove('btn-outline-secondary');
            setTimeout(() => {
                button.textContent = 'Copy';
                button.classList.remove('btn-success');
                button.classList.add('btn-outline-secondary');
            }, 2000);
        }).catch(() => {
            button.textContent = 'Failed';
            setTimeout(() => {
                button.textContent = 'Copy';
            }, 2000);
        });
    });
});

// Table of Contents Highlight and Smooth Scrolling
const tocLinks = document.querySelectorAll('.toc .nav-link');
const sections = document.querySelectorAll('.content-section');

// Highlight current section in TOC
window.addEventListener('scroll', () => {
    let current = '';
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop - 120; // Account for fixed navbar
        const sectionHeight = section.clientHeight;
        if (window.pageYOffset >= sectionTop - 50) {
            current = section.getAttribute('id');
        }
    });
    
    tocLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === '#' + current) {
            link.classList.add('active');
        }
    });
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        if (searchInput) {
            searchInput.focus();
        }
    }
});

// Add search shortcut hint
if (searchInput) {
    const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
    const shortcut = isMac ? '⌘K' : 'Ctrl+K';
    searchInput.placeholder = `Search tools... (${shortcut})`;
}

// Lazy loading for images
const images = document.querySelectorAll('img[data-src]');
const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
            imageObserver.unobserve(img);
        }
    });
});

images.forEach(img => imageObserver.observe(img));

// Add loading states for dynamic content
const addLoadingState = (element) => {
    element.classList.add('loading');
    setTimeout(() => {
        element.classList.remove('loading');
    }, 500);
};

// Initialize tooltips if Bootstrap is available
if (typeof bootstrap !== 'undefined') {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
} 