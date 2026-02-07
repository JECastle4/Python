<template>
  <div class="astronomy-scene">
    <div class="scene-layout">
      <div class="map-row">
        <BaseMap v-if="!hasData" class="map-panel" :enablePinTool="true" @pin-placed="onPinPlaced" />
      </div>
      <div v-if="!hasData" class="date-range-row">
        <DateRangePicker
          class="date-range-panel"
          :initialStartDate="params.start_date"
          :initialEndDate="params.end_date"
          @update:dates="onDateRangeSelected"
        />
      </div>
      <canvas v-if="hasData" ref="canvasRef" class="canvas-panel" />
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
        
        <div class="form-group frames-per-day-group">
          <label>Frames per day:</label>
          <input
            v-model.number="framesPerDay"
            type="range"
            min="1"
            max="1440"
            step="1"
          />
          <span>{{ framesPerDay }} frames/day</span>
        </div>

        <div class="form-group">
          <label>Frame Count:</label>
          <input
            v-model.number="params.frame_count"
            type="number"
            min="1"
            required
            readonly
          />
          <span>{{ params.frame_count }} total frames</span>
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
            <p><strong>Sun Alt:</strong> {{ typeof currentFrame.sun.altitude === 'number' ? currentFrame.sun.altitude.toFixed(1) : 'N/A' }}°</p>
            <p><strong>Sun Visible:</strong> {{ currentFrame.sun.is_visible ? 'Yes' : 'No' }}</p>
            <p><strong>Moon Alt:</strong> {{ typeof currentFrame.moon.altitude === 'number' ? currentFrame.moon.altitude.toFixed(1) : 'N/A' }}°</p>
            <p><strong>Moon Visible:</strong> {{ currentFrame.moon.is_visible ? 'Yes' : 'No' }}</p>
          <p><strong>Moon Phase:</strong> {{ currentFrame.moon_phase.phase_name }}</p>
          <p><strong>Illumination:</strong> {{ (currentFrame.moon_phase.illumination * 100).toFixed(1) }}%</p>
        </div>
      </div>
    </div>
  </div>
</div>  
</template>

<script setup lang="ts">
import { defineAsyncComponent } from 'vue';
const BaseMap = defineAsyncComponent(() => import('./BaseMap.vue'));
const DateRangePicker = defineAsyncComponent(() => import('./DateRangePicker.vue'));

// Form parameters with defaults
const today = new Date();
const yyyy = today.getFullYear();
const mm = String(today.getMonth() + 1).padStart(2, '0');
const dd = String(today.getDate()).padStart(2, '0');
const startDate = `${yyyy}-${mm}-${dd}`;
const endDate = `${yyyy}-${mm}-${dd}`;

const params = ref({
  latitude: 51.5,
  longitude: -0.1,
  start_date: startDate,
  start_time: '00:00:00',
  end_date: endDate,
  end_time: '23:59:59',
  frame_count: 48,
});

const framesPerDay = ref(48);

// Canvas reference
const canvasRef = ref<HTMLCanvasElement | null>(null);
// API data
const { data, loading, error, hasData, frameCount, fetchBatchObservations, clearData: clearApiData } = useAstronomyData();
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

function calculateDaysInRange() {
  const start = new Date(params.value.start_date);
  const end = new Date(params.value.end_date);

  // Form parameters with defaults
  const msPerDay = 24 * 60 * 60 * 1000;
  return Math.floor((end.getTime() - start.getTime()) / msPerDay) + 1;
}

function updateFrameCount() {
  const days = calculateDaysInRange();
  params.value.frame_count = days * framesPerDay.value;
}

// Watch for changes in date range or framesPerDay
import { watch } from 'vue';
watch([
  () => params.value.start_date,
  () => params.value.end_date,
  framesPerDay
], updateFrameCount, { immediate: true });

function onPinPlaced({ lat, lon }: { lat: number; lon: number }) {
  params.value.latitude = lat;
  params.value.longitude = lon;
}

function onDateRangeSelected(dates: { start: Date, end: Date }) {
  // Format as YYYY-MM-DD for params
  params.value.start_date = dates.start.toISOString().slice(0, 10);
  params.value.end_date = dates.end.toISOString().slice(0, 10);
}

import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useAstronomyData } from '@/composables/useAstronomyData';
import { SceneManager } from '@/three/scene';
import { Sun } from '@/three/objects/Sun';
import { Moon } from '@/three/objects/Moon';
import { Earth } from '@/three/objects/Earth';
import type { ObservationFrame } from '@/types/api.types';

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


const initializeObjects = () => {
  if (!canvasRef.value) return;
  if (!earth || !sun || !moon || !sceneManager) {
    sceneManager = new SceneManager(canvasRef.value);
    earth = new Earth();
    sun = new Sun();
    moon = new Moon();
    earth.addToScene(sceneManager.scene);
    sun.addToScene(sceneManager.scene);
    moon.addToScene(sceneManager.scene);
    // Hide objects until data is loaded
    if (earth && earth.mesh && earth.getGridHelper() && earth.getAxesHelper() && earth.getHemisphereGrid()) {
      earth.mesh.visible = false;
      earth.getGridHelper().visible = false;
      earth.getAxesHelper().visible = false;
      earth.getHemisphereGrid().visible = false;
    }
    if (sun && sun.mesh && sun.getLight()) {
      sun.mesh.visible = false;
      sun.getLight().visible = false;
    }
    if (moon && moon.mesh) {
      moon.mesh.visible = false;
    }
    sceneManager.startAnimation(updateAnimation);
  }
};

import { nextTick } from 'vue';

// Initialize Three.js scene when canvas is available (hasData becomes true)
watch(
  () => hasData.value,
  (newVal) => {
    if (newVal) {
      nextTick(() => {
        // Vue will set canvasRef.value after DOM update
        if (canvasRef.value) {
          initializeObjects();
        } else {
          // If still not set, try again on next tick
          nextTick(() => {
            if (canvasRef.value) {
              initializeObjects();
            }
          });
        }
      });
    }
  }
);

// Add window resize event listener on mount
onMounted(() => {
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
    if (!canvasRef.value) {
      await nextTick();
      // If still not set, manually query the DOM for the canvas
      if (!canvasRef.value) {
        const domCanvas = document.querySelector('.canvas-panel');
        if (domCanvas instanceof HTMLCanvasElement) {
          canvasRef.value = domCanvas;
        }
      }
    }
    if (!sun || !moon || !earth || !sceneManager) {
      initializeObjects();
    }
    currentIndex.value = 0;
    calculateFrameInterval();
    updatePositions();
    // Set visibility for first frame from API data
    const frame = currentFrame.value;
    if (frame) {
      if (earth) {
        earth.mesh.visible = true;
        earth.getGridHelper().visible = true;
        earth.getAxesHelper().visible = true;
        earth.getHemisphereGrid().visible = false;
      }
      if (sun) {
        sun.mesh.visible = frame.sun.is_visible;
        sun.getLight().visible = frame.sun.is_visible;
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
    // Only show sun in 3D view if above horizon
    sun.mesh.visible = (viewMode.value === 'SKY') ? frame.sun.is_visible : frame.sun.is_visible;
    sun.getLight().visible = (viewMode.value === 'SKY') ? frame.sun.is_visible : frame.sun.is_visible;
    if (viewMode.value === '3D') {
      // Optionally: Only show sun in 3D if above horizon
      sun.mesh.visible = frame.sun.is_visible;
      sun.getLight().visible = frame.sun.is_visible;
    } else {
      sun.mesh.visible = frame.sun.is_visible;
      sun.getLight().visible = frame.sun.is_visible;
    }
  }
  if (moon) {
    moon.mesh.visible = frame.moon.is_visible;
  }
  if (earth) {
    // Earth is always visible during animation
    earth.mesh.visible = true;
    earth.getGridHelper().visible = true;
    earth.getAxesHelper().visible = true;
    earth.getHemisphereGrid().visible = (viewMode.value === 'SKY');
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
  if (sceneManager && earth && sun && moon) {
    sceneManager.setViewMode(mode);
    earth.setViewMode(mode);
    sun.setViewMode(mode.toLowerCase() as 'sky' | '3d');
    moon.setViewMode(mode.toLowerCase() as 'sky' | '3d');
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
    earth.getGridHelper().visible = false;
    earth.getAxesHelper().visible = false;
    earth.getHemisphereGrid().visible = false;
  }
  if (sun) {
    sun.mesh.visible = false;
    sun.getLight().visible = false;
  }
  if (moon) {
    moon.mesh.visible = false;
  }
}

function clearData() {
  isAnimating.value = false;
  currentIndex.value = 0;
  clearApiData();
  // Dispose and null out scene objects so they are recreated on next load
  if (sceneManager) {
    sceneManager.dispose();
    sceneManager = null;
  }
  sun = null;
  moon = null;
  earth = null;
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
}

.scene-layout {
  width: 100%;
  height: 100%;
  position: relative;
}
.map-row {
  width: 100%;
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: flex-start;
}
.map-panel {
  width: 60vw;
  max-width: 900px;
  min-width: 350px;
  height: 400px;
  min-height: 400px;
  max-height: 400px;
  margin-top: 16px;
  margin-left: 16px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.12);
}
.canvas-panel {
  width: 100%;
  height: 100%;
}

.map-panel {
  flex: 1 1 0;
  min-width: 350px;
  max-width: 700px;
  height: 100%;
}

.canvas-panel {
  flex: 1 1 0;
  width: 100%;
  height: 100%;
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
.scene-layout {
  display: flex;
  flex-direction: column;
}

.map-row {
  display: block;
}

.map-panel {
  min-width: 300px;
  width: 100%;
}

.date-range-row {
  margin-top: 12px;
  width: 100%;
  display: flex;
  justify-content: flex-start;
}

.date-range-panel {
  min-width: 220px;
  max-width: 350px;
  width: 100%;
}

@media (max-width: 600px) {
  .scene-layout {
    padding: 8px;
  }
  .map-panel, .date-range-panel {
    min-width: 0;
    width: 100%;
    max-width: 100%;
  }
}
</style>
