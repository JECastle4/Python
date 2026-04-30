<template>
  <div class="moon-phase-indicator">
    <canvas ref="moonPhase3D" width="80" height="80" style="display: block; margin: 0 auto; background: #222; border-radius: 50%; box-shadow: 0 0 8px #111;" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue';
import * as THREE from 'three';

const props = defineProps<{
  phaseAngle: number; // in degrees
  elongationAngle?: number; // in degrees, 0=new, 180=full
  brightLimbAngle?: number; // in degrees, east of north
}>();

const moonPhase3D = ref<HTMLCanvasElement | null>(null);
let renderer: THREE.WebGLRenderer | null = null;
let scene: THREE.Scene | null = null;
let camera: THREE.PerspectiveCamera | null = null;
let moonMesh: THREE.Mesh | null = null;
let moonMaterial: THREE.ShaderMaterial | null = null;

function renderScene() {
  if (renderer && scene && camera) {
    renderer.render(scene, camera);
  }
}

function disposeMoonPhaseScene() {
  if (scene) {
    scene.traverse((object) => {
      const mesh = object as THREE.Mesh;
      if (mesh.geometry) {
        mesh.geometry.dispose();
      }
      const material = mesh.material;
      if (Array.isArray(material)) {
        material.forEach((m) => m.dispose());
      } else if (material) {
        material.dispose();
      }
    });
  }

  if (renderer) {
    renderer.dispose();
  }

  renderer = null;
  scene = null;
  camera = null;
  moonMesh = null;
  moonMaterial = null;
}

function setupMoonPhaseScene() {
  if (!moonPhase3D.value) return;

  let hasWebGL = false;
  try {
    hasWebGL = !!(moonPhase3D.value.getContext('webgl2') || moonPhase3D.value.getContext('webgl'));
  } catch {
    hasWebGL = false;
  }
  if (!hasWebGL) return;

  disposeMoonPhaseScene();
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(30, 1, 0.1, 10);
  camera.position.set(0, 0, 3);
  camera.lookAt(0, 0, 0);

  // Moon sphere
  const geometry = new THREE.SphereGeometry(1, 48, 48);
  moonMaterial = new THREE.ShaderMaterial({
    uniforms: {
      uLightDir: { value: new THREE.Vector3(0, 0, -1) },
      uLitColor: { value: new THREE.Color(0xffffff) },
      uDarkColor: { value: new THREE.Color(0x0f0f0f) },
    },
    vertexShader: `
      varying vec3 vNormal;
      void main() {
        vNormal = normalize(normalMatrix * normal);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform vec3 uLightDir;
      uniform vec3 uLitColor;
      uniform vec3 uDarkColor;
      varying vec3 vNormal;
      void main() {
        float ndl = dot(normalize(vNormal), normalize(uLightDir));
        float lit = step(0.0, ndl);
        vec3 color = mix(uDarkColor, uLitColor, lit);
        gl_FragColor = vec4(color, 1.0);
      }
    `,
  });
  moonMaterial.side = THREE.FrontSide;
  moonMesh = new THREE.Mesh(geometry, moonMaterial);
  scene.add(moonMesh);

  try {
    renderer = new THREE.WebGLRenderer({ canvas: moonPhase3D.value, alpha: true, antialias: true });
  } catch {
    renderer = null;
    return;
  }
  renderer.setSize(80, 80, false);
  renderer.setClearColor(0x222222, 1);

  updateLighting();
  renderScene();
}

function updateLighting() {
  if (!moonMaterial) return;
  const normalizedPhase = ((props.phaseAngle % 360) + 360) % 360;
  const fallbackElongation = normalizedPhase <= 180 ? normalizedPhase : 360 - normalizedPhase;
  const elongation = props.elongationAngle ?? fallbackElongation;
  const elongationRad = (elongation * Math.PI) / 180;
  const limbRad = ((props.brightLimbAngle ?? 0) * Math.PI) / 180;

  // Bright limb angle already encodes waxing/waning orientation in the sky.
  const lightInPlane = Math.sin(elongationRad);
  const lightZ = -Math.cos(elongationRad);

  // Position angle is measured north through east; for sky-disk rendering, east is screen-left.
  const rotatedX = -lightInPlane * Math.sin(limbRad);
  const rotatedY = lightInPlane * Math.cos(limbRad);
  console.log(rotatedX, rotatedY, lightZ);
  const lightDir = moonMaterial.uniforms.uLightDir.value as THREE.Vector3;
  lightDir.set(rotatedX, rotatedY, lightZ).normalize();
}

onMounted(() => {
  setupMoonPhaseScene();
});

onUnmounted(() => {
  disposeMoonPhaseScene();
});

watch(() => [props.phaseAngle, props.elongationAngle, props.brightLimbAngle], () => {
  updateLighting();
  renderScene();
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
