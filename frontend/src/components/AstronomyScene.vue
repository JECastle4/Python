<template>
  <div class="astronomy-scene">
    <canvas ref="canvasRef"></canvas>
    
    <div class="controls-panel">
      <h2>Sun and Moon Animation from Earth</h2>
      
      <div v-if="loading" class="loading">
        Loading data...
      </div>
      
      <div v-if="error" class="error">
        {{ error }}
      </div>
      
      <div v-if="!hasData" class="input-form">
        <div class="form-group">
          <label>Latitude:</label>
          <input 
            v-model.number="params.latitude" 
            type="number" 
            step="0.1"
            min="-90"
            max="90"
            required
            :class="{ invalid: !isLatitudeValid }"
          />
          <span v-if="!isLatitudeValid" class="error-message">
            Latitude must be between -90° and 90°
          </span>
        </div>
        
        <div class="form-group">
          <label>Longitude:</label>
          <input 
            v-model.number="params.longitude" 
            type="number" 
            step="0.1"
            min="-180"
            max="180"
            required
            :class="{ invalid: !isLongitudeValid }"
          />
          <span v-if="!isLongitudeValid" class="error-message">
            Longitude must be between -180° and 180°
          </span>
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
          <input 
            v-model.number="params.frame_count" 
            type="number" 
            min="2" 
            max="10000"
            step="1"
            required
            :class="{ invalid: !isFrameCountValid }"
          />
          <span v-if="!isFrameCountValid" class="error-message">
            Frame count must be between 2 and 10000
          </span>
        </div>
        
        <button @click="loadData" :disabled="loading || !isFormValid">Load Data</button>
      </div>
      
      <div v-if="hasData" class="animation-controls">
        <p>Frames: {{ frameCount }}</p>
        
        <div class="view-toggle">
          <button @click="setViewMode('3D')" :class="{ active: viewMode === '3D' }">
            3D View
          </button>
          <button @click="setViewMode('SKY')" :class="{ active: viewMode === 'SKY' }">
            Sky View
          </button>
        </div>
        
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
const viewMode = ref<'3D' | 'SKY'>('3D');
const lastTime = ref(0);
const frameIntervalMs = ref(1000); // Time between frames in milliseconds

// API data
const { data, loading, error, hasData, frameCount, fetchBatchObservations, clearData: clearApiData } = useAstronomyData();

// Form parameters with defaults
// TODO: Improve date/time handling - calculate intelligent start/end times based on:
//   - Sun/moon rise/set times for the location
//   - Astronomical events (dawn, dusk, twilight periods)
//   - User's timezone
//   - Suggested observation windows (e.g., "next 24 hours", "tonight", "this week")
// TODO (#10): Replace hardcoded dates with relative/dynamic dates
// test
const params = ref({
  latitude: 51.5,
  longitude: -0.1,
  start_date: '2026-02-02',  // Hardcoded - see issue #10
  start_time: '00:00:00',
  end_date: '2026-02-03',  // Hardcoded - see issue #10
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

// Form validation
const isLatitudeValid = computed(() => {
  const lat = params.value.latitude;
  return Number.isFinite(lat) && lat >= -90 && lat <= 90;
});

const isLongitudeValid = computed(() => {
  const lon = params.value.longitude;
  return Number.isFinite(lon) && lon >= -180 && lon <= 180;
});

const isFrameCountValid = computed(() => {
  const count = params.value.frame_count;
  return Number.isFinite(count) && count >= 2 && count <= 10000 && Number.isInteger(count);
});

const isFormValid = computed(() => {
  return isLatitudeValid.value && isLongitudeValid.value && isFrameCountValid.value;
});

// Initialize Three.js scene
onMounted(() => {
  if (canvasRef.value) {
    sceneManager = new SceneManager(canvasRef.value);
    earth = new Earth();
    sun = new Sun();
    moon = new Moon();
    earth.addToScene(sceneManager.scene);
    sun.addToScene(sceneManager.scene);
    moon.addToScene(sceneManager.scene);
    // Hide objects until data is loaded
    if (earth) {
      earth.mesh.visible = false;
      earth.gridHelper.visible = false;
      earth.axesHelper.visible = false;
      earth.hemisphereGrid.visible = false;
    }
    if (sun) {
      sun.mesh.visible = false;
      sun.light.visible = false;
    }
    if (moon) {
      moon.mesh.visible = false;
    }
    sceneManager.startAnimation(updateAnimation);
  }
  // Add window resize event listener
  window.addEventListener('resize', handleResize);
});

// Cleanup
onUnmounted(() => {
  if (sceneManager) {
    sceneManager.dispose();
  }
  // Remove window resize event listener
  window.removeEventListener('resize', handleResize);
});

// Load data from API
async function loadData() {
  await fetchBatchObservations(params.value);
  if (hasData.value) {
    currentIndex.value = 0;
    calculateFrameInterval();
    updatePositions();
    // Set visibility for first frame from API data
    const frame = currentFrame.value;
    if (frame) {
      if (earth) {
        earth.mesh.visible = true;
        earth.gridHelper.visible = true;
        earth.axesHelper.visible = true;
        earth.hemisphereGrid.visible = false;
      }
      if (sun) {
        sun.mesh.visible = frame.sun.is_visible;
        sun.light.visible = frame.sun.is_visible;
      }
      if (moon) {
        moon.mesh.visible = frame.moon.is_visible;
      }
    }
  }
}

// Calculate the time interval between frames based on actual datetime values
// Fixes #11: Animation now respects the actual time intervals in the data
// rather than using a fixed frame rate
function calculateFrameInterval() {
  if (!data.value || data.value.frames.length < 2) {
    frameIntervalMs.value = 1000; // Default to 1 second if we can't calculate
    return;
  }
  
  // Parse the first two frame datetimes to calculate the real-time interval
  const firstFrame = new Date(data.value.frames[0].datetime);
  const secondFrame = new Date(data.value.frames[1].datetime);
  
  // Validate that the dates are valid
  if (!isFinite(firstFrame.getTime()) || !isFinite(secondFrame.getTime())) {
    frameIntervalMs.value = 1000; // Fall back to default if dates are invalid
    return;
  }
  
  // Calculate the time difference in milliseconds
  const realTimeDiffMs = secondFrame.getTime() - firstFrame.getTime();
  
  // Validate that the time difference is positive
  if (realTimeDiffMs <= 0) {
    console.warn('Frame timestamps are not in chronological order or are identical. Using default interval.');
    frameIntervalMs.value = 1000; // Fall back to default if frames are out of order
    return;
  }
  
  // Scale to a reasonable animation speed (e.g., 1 real hour = 1 second of animation)
  // This gives us a base speed that makes sense for visualization
  const MILLISECONDS_PER_SECOND = 1000;
  const MILLISECONDS_PER_HOUR = 60 * 60 * 1000;
  const scaleFactor = MILLISECONDS_PER_SECOND / MILLISECONDS_PER_HOUR;
  frameIntervalMs.value = realTimeDiffMs * scaleFactor;
  
  // Ensure a minimum interval to prevent too-fast animations
  frameIntervalMs.value = Math.max(frameIntervalMs.value, 50);
}

// Update celestial object positions
function updatePositions() {
  const frame = currentFrame.value;
  if (!frame || !sun || !moon) return;
  
  // Update visibility based on frame data
  if (sun) {
    sun.mesh.visible = frame.sun.is_visible;
    sun.light.visible = frame.sun.is_visible;
  }
  if (moon) {
    moon.mesh.visible = frame.moon.is_visible;
  }
  if (earth) {
    // Earth is always visible during animation
    earth.mesh.visible = true;
    earth.gridHelper.visible = true;
    earth.axesHelper.visible = true;
    earth.hemisphereGrid.visible = (viewMode.value === 'SKY');
  }

  sun.updatePosition(
    frame.sun.azimuth,
    frame.sun.altitude,
    frame.sun.is_visible,
    viewMode.value
  );

  moon.updatePosition(
    frame.moon.azimuth,
    frame.moon.altitude,
    frame.moon.is_visible,
    viewMode.value
  );

  moon.updatePhase(frame.moon_phase.illumination * 100);
}

// Switch view mode
function setViewMode(mode: '3D' | 'SKY') {
  viewMode.value = mode;
  
  if (sceneManager && earth) {
    sceneManager.setViewMode(mode);
    earth.setViewMode(mode);
    updatePositions();
  }
}

// Animation loop callback
function updateAnimation() {
  if (!isAnimating.value || !data.value) return;
  
  const now = Date.now();
  const delta = now - lastTime.value;
  
  // Use calculated frame interval scaled by animation speed
  // Higher speed = shorter interval = faster animation
  const interval = frameIntervalMs.value / animationSpeed.value;
  
  if (delta > interval) {
    lastTime.value = now;
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
    lastTime.value = Date.now();
  }
}

function resetAnimation() {
  isAnimating.value = false;
  currentIndex.value = 0;
  updatePositions();
  // Hide objects on reset
  if (earth) {
    earth.mesh.visible = false;
    earth.gridHelper.visible = false;
    earth.axesHelper.visible = false;
    earth.hemisphereGrid.visible = false;
  }
  if (sun) {
    sun.mesh.visible = false;
    sun.light.visible = false;
  }
  if (moon) {
    moon.mesh.visible = false;
  }
}

function clearData() {
  isAnimating.value = false;
  currentIndex.value = 0;
  clearApiData();
  // Hide objects on clear
  if (earth) {
    earth.mesh.visible = false;
    earth.gridHelper.visible = false;
    earth.axesHelper.visible = false;
    earth.hemisphereGrid.visible = false;
  }
  if (sun) {
    sun.mesh.visible = false;
    sun.light.visible = false;
  }
  if (moon) {
    moon.mesh.visible = false;
  }
}

// Window resize event handler
function handleResize() {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const parent = canvas.parentElement;
  const dpr = window.devicePixelRatio || 1;
  const width = (parent?.clientWidth || window.innerWidth);
  const height = (parent?.clientHeight || window.innerHeight);
  // Set canvas rendering size for high-DPI
  canvas.width = width * dpr;
  canvas.height = height * dpr;
  // Set CSS size
  canvas.style.width = width + 'px';
  canvas.style.height = height + 'px';
  // Update Three.js renderer and camera if available
  if (sceneManager) {
    sceneManager.renderer.setSize(width, height, false);
    sceneManager.camera.aspect = width / height;
    sceneManager.camera.updateProjectionMatrix();
  }
}
</script>

<style scoped>
.astronomy-scene {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

html, body, #app {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
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

.form-group input.invalid {
  border-color: #ff4444;
  background: #331111;
}

.error-message {
  display: block;
  color: #ff4444;
  font-size: 0.8em;
  margin-top: 4px;
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

.view-toggle {
  display: flex;
  gap: 5px;
  margin-bottom: 15px;
}

.view-toggle button {
  flex: 1;
  margin-bottom: 0;
  background: #333;
}

.view-toggle button.active {
  background: #0066cc;
  font-weight: bold;
}

.view-toggle button:hover:not(.active) {
  background: #444;
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
