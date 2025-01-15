import * as THREE from 'https://cdn.skypack.dev/three@0.136.0';

let scene, camera, renderer;
let geometry, material, mesh;
let time = 0;

function init() {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 1.5;

    renderer = new THREE.WebGLRenderer({
        canvas: document.getElementById('bg'),
        alpha: true,
        antialias: true
    });
    renderer.setSize(window.innerWidth, window.innerHeight);

    // Create abstract flowing geometry
    geometry = new THREE.TorusKnotGeometry(0.8, 0.3, 100, 16);

    // Create custom shader material
    material = new THREE.ShaderMaterial({
        uniforms: {
            time: { value: 0 },
            resolution: { value: new THREE.Vector2(window.innerWidth, window.innerHeight) }
        },
        vertexShader: `
            varying vec2 vUv;
            varying vec3 vPosition;
            uniform float time;
            
            void main() {
                vUv = uv;
                vPosition = position;
                
                // Create flowing movement
                vec3 pos = position;
                float displacement = sin(pos.x * 2.0 + time) * 
                                   cos(pos.y * 2.0 + time) * 
                                   sin(pos.z * 2.0 + time) * 0.2;
                
                pos += normal * displacement;
                
                gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
            }
        `,
        fragmentShader: `
            varying vec2 vUv;
            varying vec3 vPosition;
            uniform float time;
            
            void main() {
                // Create flowing gradient effect
                vec3 color1 = vec3(0.0, 0.8, 1.0); // Cyan
                vec3 color2 = vec3(0.8, 0.0, 1.0); // Purple
                vec3 color3 = vec3(0.0, 1.0, 0.5); // Green
                
                float noise = sin(vPosition.x * 5.0 + time) * 
                             cos(vPosition.y * 5.0 + time) * 
                             sin(vPosition.z * 5.0 + time);
                
                vec3 finalColor = mix(
                    mix(color1, color2, sin(time * 0.5) * 0.5 + 0.5),
                    color3,
                    noise * 0.5 + 0.5
                );
                
                // Add glow effect
                float glow = 0.8 + 0.2 * sin(time + vPosition.x * 2.0);
                
                gl_FragColor = vec4(finalColor * glow, 0.7);
            }
        `,
        transparent: true,
        side: THREE.DoubleSide
    });

    mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);
}

function animate() {
    requestAnimationFrame(animate);
    time += 0.01;

    // Rotate the geometry
    mesh.rotation.x = time * 0.2;
    mesh.rotation.y = time * 0.3;

    // Update shader uniforms
    material.uniforms.time.value = time;

    // Add smooth camera movement
    camera.position.x = Math.sin(time * 0.2) * 0.3;
    camera.position.y = Math.cos(time * 0.3) * 0.3;
    camera.lookAt(scene.position);

    renderer.render(scene, camera);

    // Add particle animation
    particles.children.forEach((particle, i) => {
        particle.position.y += Math.sin(time + i) * 0.001;
        particle.material.opacity = 0.5 + Math.sin(time + i) * 0.2;
    });
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
    material.uniforms.resolution.value.set(window.innerWidth, window.innerHeight);
}

window.addEventListener('resize', onWindowResize, false);
window.addEventListener('DOMContentLoaded', () => {
    init();
    animate();
});

function createJobCards() {
    const cardGeometry = new THREE.PlaneGeometry(1, 0.6);
    const cardMaterial = new THREE.ShaderMaterial({
        uniforms: {
            time: { value: 0 },
            hover: { value: 0.0 }
        },
        vertexShader: `
            varying vec2 vUv;
            uniform float hover;
            void main() {
                vec3 pos = position;
                pos.z += hover * 0.1 * sin(pos.x * 10.0);
                gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
                vUv = uv;
            }
        `,
        fragmentShader: `
            varying vec2 vUv;
            uniform float hover;
            void main() {
                vec3 color = mix(
                    vec3(0.0, 0.8, 1.0),
                    vec3(0.0, 1.0, 0.5),
                    vUv.x + hover
                );
                gl_FragColor = vec4(color, 0.7);
            }
        `,
        transparent: true,
        side: THREE.DoubleSide
    });
    return new THREE.Mesh(cardGeometry, cardMaterial);
}

function createInteractiveBackground() {
    const particles = new THREE.Group();
    const particleCount = 50;
    
    for (let i = 0; i < particleCount; i++) {
        const particle = new THREE.Mesh(
            new THREE.SphereGeometry(0.02, 8, 8),
            new THREE.MeshBasicMaterial({
                color: new THREE.Color(0x00ff87),
                transparent: true,
                opacity: 0.5
            })
        );
        
        particle.position.set(
            (Math.random() - 0.5) * 5,
            (Math.random() - 0.5) * 5,
            (Math.random() - 0.5) * 5
        );
        
        particles.add(particle);
    }
    
    scene.add(particles);
    return particles;
} 