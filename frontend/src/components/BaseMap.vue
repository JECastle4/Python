<template>
  <div ref="mapContainer" class="ol-map"></div>
</template>

<script setup>
import { onMounted, ref, onBeforeUnmount } from 'vue'
import 'ol/ol.css'
import Map from 'ol/Map'
import View from 'ol/View'
import TileLayer from 'ol/layer/Tile'
import OSM from 'ol/source/OSM'
import Zoom from 'ol/control/Zoom'
import Attribution from 'ol/control/Attribution'

const mapContainer = ref(null)
let mapInstance = null

onMounted(() => {
  mapInstance = new Map({
    target: mapContainer.value,
    layers: [
      new TileLayer({
        source: new OSM(),
      }),
    ],
    view: new View({
      center: [0, 0], // [lon, lat] in EPSG:3857
      zoom: 2,
    }),
    controls: [
      new Zoom(),
      new Attribution({
        collapsible: false,
        className: 'ol-attribution bottom-left',
      }),
    ],
  })
})

onBeforeUnmount(() => {
  if (mapInstance) {
    mapInstance.setTarget(null)
    mapInstance = null
  }
})
</script>

<style scoped>
.ol-map {
  width: 100%;
  height: 100%;
  min-height: 400px;
  border: 1px solid #ccc;
}

:deep(.ol-viewport) {
  height: 400px !important;
  min-height: 400px !important;
}

.ol-attribution.bottom-left {
  left: 8px !important;
  right: auto !important;
  bottom: 8px !important;
  top: auto !important;
  background: rgba(255,255,255,0.9);
  color: #333;
  font-size: 0.85em;
  border-radius: 4px;
  padding: 2px 8px;
  z-index: 1000 !important;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  display: block !important;
}
/* Ensure OpenLayers attribution is always visible */
.ol-attribution {
  opacity: 1 !important;
  visibility: visible !important;
  z-index: 1000 !important;
}
</style>
