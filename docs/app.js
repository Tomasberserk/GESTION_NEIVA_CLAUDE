// ============================================
// CONFIGURADOR INTELIGENTE DE SOFTWARE
// ============================================

const tierConfig = {
    basic: {
        baseCost: 300,
        deliveryTime: '24 horas',
        maxFeatures: 2,
    },
    medium: {
        baseCost: 1500,
        deliveryTime: '72 horas',
        maxFeatures: 5,
    },
    professional: {
        baseCost: 5000,
        deliveryTime: '1-2 semanas',
        maxFeatures: 8,
    },
};

const featuresCosts = {
    'multi-tenant': 200,
    'inventory': 300,
    'billing': 400,
    'suppliers': 250,
    'reporting': 150,
    'payment': 350,
};

// ============================================
// INICIALIZACIÓN
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    initConfigurador();
    initCounterAnimation();
    initFormHandler();
});

// ============================================
// CONFIGURADOR
// ============================================

function initConfigurador() {
    const checkboxes = document.querySelectorAll('.feature-input');
    
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateConfigurador);
    });
    
    // Inicialización
    updateConfigurador();
}

function updateConfigurador() {
    const selectedFeatures = Array.from(document.querySelectorAll('.feature-input:checked'))
        .map(cb => cb.value);
    
    // Calcular costo de características
    const addonCost = selectedFeatures.reduce((sum, feature) => sum + (featuresCosts[feature] || 0), 0);
    
    // Determinar tier
    const tier = determineTier(selectedFeatures.length, addonCost);
    const tierData = tierConfig[tier];
    
    // Calcular costo total
    const totalCost = tierData.baseCost + addonCost;
    
    // Actualizar UI
    updateTierDisplay(tier);
    updatePriceBreakdown(tierData.baseCost, addonCost, totalCost);
    updateDeliveryTime(tierData.deliveryTime);
    updateComparison(totalCost);
}

function determineTier(featureCount, addonCost) {
    if (featureCount >= 4 || addonCost > 2000) {
        return 'professional';
    } else if (featureCount >= 2 || addonCost > 500) {
        return 'medium';
    }
    return 'basic';
}

function updateTierDisplay(tier) {
    // Remover clase active de todos
    document.querySelectorAll('.tier-badge').forEach(badge => {
        badge.classList.remove('active');
    });
    
    // Agregar clase active al tier seleccionado
    const tierMap = {
        'basic': '#badge-basic',
        'medium': '#badge-medium',
        'professional': '#badge-professional',
    };
    
    const activeBadge = document.querySelector(tierMap[tier]);
    if (activeBadge) {
        activeBadge.classList.add('active');
    }
    
    // Actualizar texto del tier
    document.getElementById('tier-display').textContent = 
        tier.charAt(0).toUpperCase() + tier.slice(1);
    
    // Animación suave
    animateValue(document.getElementById('tier-display'));
}

function updatePriceBreakdown(basePrice, addonPrice, totalPrice) {
    const basePriceEl = document.getElementById('base-price');
    const addonPriceEl = document.getElementById('addon-price');
    const totalPriceEl = document.getElementById('total-price');
    
    animateNumberChange(basePriceEl, parseInt(basePriceEl.textContent), basePrice);
    animateNumberChange(addonPriceEl, parseInt(addonPriceEl.textContent), addonPrice);
    animateNumberChange(totalPriceEl, parseInt(totalPriceEl.textContent), totalPrice);
}

function updateDeliveryTime(deliveryTime) {
    const deliveryEl = document.getElementById('delivery-time');
    deliveryEl.style.opacity = '0';
    
    setTimeout(() => {
        deliveryEl.textContent = deliveryTime;
        deliveryEl.style.opacity = '1';
        deliveryEl.style.transition = 'opacity 0.3s ease-out';
    }, 150);
}

function updateComparison(totalPrice) {
    const traditionalCost = 10000; // Costo promedio tradicional
    const savingsPercent = Math.round(((traditionalCost - totalPrice) / traditionalCost) * 100);
    const comparePriceEl = document.getElementById('compare-ia');
    const savingsPercentEl = document.getElementById('savings-percent');
    
    // Actualizar precio en la barra de comparación
    const barWidth = Math.max((totalPrice / traditionalCost) * 100, 3);
    const barIa = document.querySelector('.bar-ia');
    barIa.style.width = barWidth + '%';
    
    animateNumberChange(comparePriceEl, parseInt(comparePriceEl.textContent), totalPrice);
    animateNumberChange(savingsPercentEl, parseInt(savingsPercentEl.textContent), savingsPercent);
}

// ============================================
// ANIMACIÓN DE NÚMEROS
// ============================================

function animateNumberChange(element, startValue, endValue, duration = 500) {
    if (startValue === endValue) return;
    
    const difference = endValue - startValue;
    const startTime = Date.now();
    
    function update() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeOutValue = 1 - Math.pow(1 - progress, 3); // Ease-out cubic
        
        const currentValue = Math.round(startValue + difference * easeOutValue);
        element.textContent = currentValue.toString();
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    update();
}

function animateValue(element) {
    element.style.transform = 'scale(1.1)';
    element.style.transition = 'transform 0.3s ease-out';
    
    setTimeout(() => {
        element.style.transform = 'scale(1)';
    }, 100);
}

// ============================================
// CONTADOR ANIMADO EN SCROLL (IntersectionObserver)
// ============================================

function initCounterAnimation() {
    const statValues = document.querySelectorAll('.stat-value[data-target]');
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px',
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.dataset.animated) {
                entry.target.dataset.animated = 'true';
                const targetValue = parseFloat(entry.target.dataset.target);
                animateCounter(entry.target, targetValue);
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    statValues.forEach(element => observer.observe(element));
}

function animateCounter(element, targetValue) {
    const startValue = 0;
    const duration = 1500;
    const startTime = Date.now();
    
    function update() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeOutValue = 1 - Math.pow(1 - progress, 3);
        
        const currentValue = startValue + (targetValue - startValue) * easeOutValue;
        
        // Formatar el valor
        if (targetValue < 100) {
            element.textContent = currentValue.toFixed(1);
        } else {
            element.textContent = Math.round(currentValue).toLocaleString();
        }
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    update();
}

// ============================================
// FORMULARIO DE CONTACTO
// ============================================

function initFormHandler() {
    const form = document.getElementById('lead-form');
    
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }
}

function handleFormSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const message = document.getElementById('form-message');
    
    // Validación básica
    const empresa = document.getElementById('empresa').value.trim();
    const email = document.getElementById('email').value.trim();
    const ciudad = document.getElementById('ciudad').value.trim();
    const descripcion = document.getElementById('descripcion').value.trim();
    const terminos = document.querySelector('input[name="terminos"]').checked;
    
    if (!empresa || !email || !ciudad || !descripcion) {
        showFormMessage('Por favor completa todos los campos requeridos', 'error');
        return;
    }
    
    if (!isValidEmail(email)) {
        showFormMessage('Por favor ingresa un email válido', 'error');
        return;
    }
    
    if (!terminos) {
        showFormMessage('Por favor acepta los términos y condiciones', 'error');
        return;
    }
    
    // Simular envío
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = 'Enviando...';
    
    // Simular respuesta del servidor (en producción, enviar a servidor real)
    setTimeout(() => {
        // Recopilar datos del configurador
        const selectedFeatures = Array.from(document.querySelectorAll('.feature-input:checked'))
            .map(cb => cb.value)
            .join(', ');
        
        const tier = document.getElementById('tier-display').textContent;
        const totalPrice = document.getElementById('total-price').textContent;
        const deliveryTime = document.getElementById('delivery-time').textContent;
        
        // Datos completos para enviar
        const formData = {
            empresa,
            email,
            telefono: document.getElementById('telefono').value,
            ciudad,
            descripcion,
            features: selectedFeatures,
            tier,
            estimatedCost: totalPrice,
            deliveryTime,
            timestamp: new Date().toISOString(),
        };
        
        // Aquí iría el envío real al servidor
        console.log('Datos del formulario:', formData);
        
        // Mostrar éxito
        showFormMessage(
            '✓ ¡Solicitud enviada exitosamente! Nos pondremos en contacto dentro de 24 horas.',
            'success'
        );
        
        // Resetear formulario
        form.reset();
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }, 1500);
}

function showFormMessage(text, type) {
    const message = document.getElementById('form-message');
    message.textContent = text;
    message.className = `form-message ${type}`;
    
    // Auto-ocultar mensaje después de 5 segundos
    setTimeout(() => {
        message.className = 'form-message';
    }, 5000);
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// ============================================
// SCROLL SUAVE AUXILIAR
// ============================================

function scrollToForm() {
    const form = document.getElementById('lead-form');
    if (form) {
        form.scrollIntoView({ behavior: 'smooth' });
    }
}

// ============================================
// EFECTOS ADICIONALES (OPCIONAL)
// ============================================

// Efecto de parallax suave en hero
document.addEventListener('scroll', () => {
    const hero = document.querySelector('.hero');
    if (hero) {
        const scrolled = window.pageYOffset;
        hero.style.backgroundPosition = `0px ${scrolled * 0.3}px`;
    }
});

// Lazy load para imágenes futuras
document.addEventListener('DOMContentLoaded', () => {
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });
    images.forEach(img => imageObserver.observe(img));
});

// Animación de entrada para elementos
const elementsToAnimate = document.querySelectorAll('.portfolio-card, .stat-card');
const elementObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry, index) => {
        if (entry.isIntersecting) {
            setTimeout(() => {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }, index * 100);
        }
    });
}, { threshold: 0.1 });

elementsToAnimate.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
    elementObserver.observe(el);
});
