<template>
  <div class="moon-phase-indicator">
    <canvas ref="moonPhase3D" width="80" height="80" style="display: block; margin: 0 auto; background: #222; border-radius: 50%; box-shadow: 0 0 8px #111;" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import * as THREE from 'three';

const props = defineProps<{
  phaseAngle: number; // in degrees
}>();

const moonPhase3D = ref<HTMLCanvasElement | null>(null);
let renderer: THREE.WebGLRenderer | null = null;
let scene: THREE.Scene | null = null;
let camera: THREE.PerspectiveCamera | null = null;
let moonMesh: THREE.Mesh | null = null;
let light: THREE.DirectionalLight | null = null;

function setupMoonPhaseScene() {
  if (!moonPhase3D.value) return;
  // Clean up previous renderer if any
  if (renderer) {
    renderer.dispose();
    renderer = null;
  }
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(30, 1, 0.1, 10);
  camera.position.set(0, 0, 3);
  camera.lookAt(0, 0, 0);

  // Moon sphere
  const geometry = new THREE.SphereGeometry(1, 48, 48);
  const material = new THREE.MeshPhongMaterial({ color: 0xffffff, shininess: 5, specular : 0xffffff});
  material.side = THREE.FrontSide;
  moonMesh = new THREE.Mesh(geometry, material);
  scene.add(moonMesh);

  // Directional light for phase
  light = new THREE.DirectionalLight(0xffffff, 1.0);
  light.target.position.set(0, 0, 0);
  scene.add(light);
  scene.add(light.target);

  // Ambient light for subtle fill
  //scene.add(new THREE.AmbientLight(0xffffff, 1.0));

  renderer = new THREE.WebGLRenderer({ canvas: moonPhase3D.value, alpha: true, antialias: true });
  renderer.setSize(80, 80, false);
  renderer.setClearColor(0x222222, 1);

  updateLighting();
  renderer.render(scene, camera);
}

function updateLighting() {
  if (!light) return;
  // Phase angle: 0 = new moon (sun behind moon), 180 = full moon (sun in front)
  const phaseRad = (props.phaseAngle * Math.PI) / 180;
  // Light rotates around Y axis
  console.log(phaseRad, -Math.sin(phaseRad), -Math.cos(phaseRad));
  light.position.set(-Math.sin(phaseRad),0,  -Math.cos(phaseRad));
  light.position.normalize();
  // Rotate the moon so the terminator is correct
  //if (moonMesh) {
  //  moonMesh.rotation.y = phaseRad;
  //}
}

onMounted(() => {
  setupMoonPhaseScene();
});

watch(() => props.phaseAngle, () => {
  updateLighting();
  if (renderer && scene && camera) {
    renderer.render(scene, camera);
  }
});
</script>

<style scoped>
.moon-phase-indicator {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 8px;
  margin-bottom: 8px;
}
</style>
