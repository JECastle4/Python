<template>
  <div class="astronomy-scene">
    <canvas ref="canvasRef"></canvas>
    
    <div class="controls-panel">
      <h2>Astronomy Animation</h2>
      
      <div v-if="loading" class="loading">
        Loading data...
      </div>
      
      <div v-if="error" class="error">
        {{ error }}
      </div>
      
      <div v-if="!hasData" class="input-form">
        <div class="form-group">
          <label>Latitude:</label>
          <input v-model.number="params.latitude" type="number" step="0.1" />
        </div>
        
        <div class="form-group">
          <label>Longitude:</label>
          <input v-model.number="params.longitude" type="number" step="0.1" />
        </div>
        
        <div class="form-group">
          <label>Start Date:</label>
          <input v-model="params.start_date" type="date" />
        </div>
        
        <div class="form-group">
          <label>Start Time:</label>
          <input v-model="params.start_time" type="time" step="1" />
        </div>
        
        <div class="form-group">
          <label>End Date:</label>
          <input v-model="params.end_date" type="date" />
        </div>
        
        <div class="form-group">
          <label>End Time:</label>
          <input v-model="params.end_time" type="time" step="1" />
        </div>
        
        <div class="form-group">
          <label>Frame Count:</label>
          <input v-model.number="params.frame_count" type="number" min="2" max="1000" />
        </div>
        
        <button @click="loadData" :disabled="loading">Load Data</button>
      </div>
      
      <div v-if="hasData" class="animation-controls">
        <p>Frames: {{ frameCount }}</p>
        <button @click="toggleAnimation">
          {{ isAnimating ? 'Pause' : 'Play' }}
        </button>
        <button @click="resetAnimation">Reset</button>
        <button @click="clearData">New Query</button>
        
        <div class="form-group">
          <label>Animation Speed:</label>
          <input v-model.number="animationSpeed" type="range" min="0.1" max="5" step="0.1" />
          <span>{{ animationSpeed.toFixed(1) }}x</span>
        </div>
        
        <div v-if="currentFrame" class="current-info">
          <p><strong>Time:</strong> {{ currentFrame.datetime }}</p>
          <p><strong>Sun Alt:</strong> {{ currentFrame.sun.altitude.toFixed(1) }}°</p>
          <p><strong>Sun Visible:</strong> {{ currentFrame.sun.is_visible ? 'Yes' : 'No' }}</p>
          <p><strong>Moon Alt:</strong> {{ currentFrame.moon.altitude.toFixed(1) }}°</p>
          <p><strong>Moon Visible:</strong> {{ currentFrame.moon.is_visible ? 'Yes' : 'No' }}</p>
          <p><strong>Moon Phase:</strong> {{ currentFrame.moon_phase.phase_name }}</p>
          <p><strong>Illumination:</strong> {{ (currentFrame.moon_phase.illumination * 100).toFixed(1) }}%</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useAstronomyData } from '@/composables/useAstronomyData';
import { SceneManager } from '@/three/scene';
import { Sun } from '@/three/objects/Sun';
import { Moon } from '@/three/objects/Moon';
import { Earth } from '@/three/objects/Earth';
import type { ObservationFrame } from '@/types/api.types';

// Canvas reference
const canvasRef = ref<HTMLCanvasElement | null>(null);

// Animation state
let sceneManager: SceneManager | null = null;
let sun: Sun | null = null;
let moon: Moon | null = null;
let earth: Earth | null = null;

const isAnimating = ref(false);
const animationSpeed = ref(1.0);
const currentIndex = ref(0);

// API data
const { data, loading, error, hasData, frameCount, fetchBatchObservations, clearData: clearApiData } = useAstronomyData();

// Form parameters with defaults
const params = ref({
  latitude: 51.5,
  longitude: -0.1,
  start_date: '2026-02-02',
  start_time: '00:00:00',
  end_date: '2026-02-03',
  end_time: '00:00:00',
  frame_count: 48,
});

// Current frame
const currentFrame = computed<ObservationFrame | null>(() => {
  if (!data.value || currentIndex.value >= data.value.frames.length) {
    return null;
  }
  return data.value.frames[currentIndex.value];
});

// Initialize Three.js scene
onMounted(() => {
  if (canvasRef.value) {
    sceneManager = new SceneManager(canvasRef.value);
    
    // Create celestial objects
    earth = new Earth();
    sun = new Sun();
    moon = new Moon();
    
    earth.addToScene(sceneManager.scene);
    sun.addToScene(sceneManager.scene);
    moon.addToScene(sceneManager.scene);
    
    // Start render loop
    sceneManager.startAnimation(updateAnimation);
  }
});

// Cleanup
onUnmounted(() => {
  if (sceneManager) {
    sceneManager.dispose();
  }
});

// Load data from API
async function loadData() {
  await fetchBatchObservations(params.value);
  if (hasData.value) {
    currentIndex.value = 0;
    updatePositions();
  }
}

// Update celestial object positions
function updatePositions() {
  const frame = currentFrame.value;
  if (!frame || !sun || !moon) return;
  
  sun.updatePosition(
    frame.sun.azimuth,
    frame.sun.altitude
  );
  
  moon.updatePosition(
    frame.moon.azimuth,
    frame.moon.altitude
  );
  
  moon.updatePhase(frame.moon_phase.illumination * 100);
}

// Animation loop callback
let lastTime = 0;
function updateAnimation() {
  if (!isAnimating.value || !data.value) return;
  
  const now = Date.now();
  const delta = now - lastTime;
  
  // Update every ~100ms scaled by speed
  if (delta > 100 / animationSpeed.value) {
    lastTime = now;
    currentIndex.value++;
    
    if (currentIndex.value >= data.value.frames.length) {
      currentIndex.value = 0; // Loop animation
    }
    
    updatePositions();
  }
}

function toggleAnimation() {
  isAnimating.value = !isAnimating.value;
  if (isAnimating.value) {
    lastTime = Date.now();
  }
}

function resetAnimation() {
  isAnimating.value = false;
  currentIndex.value = 0;
  updatePositions();
}

function clearData() {
  isAnimating.value = false;
  currentIndex.value = 0;
  clearApiData();
}
</script>

<style scoped>
.astronomy-scene {
  width: 100%;
  height: 100vh;
  position: relative;
  overflow: hidden;
}

canvas {
  width: 100%;
  height: 100%;
  display: block;
}

.controls-panel {
  position: absolute;
  top: 20px;
  right: 20px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 20px;
  border-radius: 8px;
  max-width: 300px;
  max-height: calc(100vh - 40px);
  overflow-y: auto;
}

.controls-panel h2 {
  margin: 0 0 15px 0;
  font-size: 1.2em;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-size: 0.9em;
}

.form-group input {
  width: 100%;
  padding: 8px;
  border: 1px solid #555;
  border-radius: 4px;
  background: #222;
  color: white;
  font-size: 0.9em;
}

button {
  width: 100%;
  padding: 10px;
  margin-bottom: 10px;
  background: #0066cc;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1em;
}

button:hover:not(:disabled) {
  background: #0052a3;
}

button:disabled {
  background: #555;
  cursor: not-allowed;
}

.loading {
  padding: 10px;
  background: rgba(255, 165, 0, 0.2);
  border-radius: 4px;
  margin-bottom: 10px;
}

.error {
  padding: 10px;
  background: rgba(255, 0, 0, 0.2);
  border: 1px solid #ff0000;
  border-radius: 4px;
  margin-bottom: 10px;
  font-size: 0.9em;
}

.current-info {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #555;
  font-size: 0.85em;
}

.current-info p {
  margin: 5px 0;
}
</style>
