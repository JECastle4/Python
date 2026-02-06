<template>
  <div ref="mapContainer" class="ol-map"></div>
</template>

<script setup>
// Custom OpenLayers control for pin tool
import Control from 'ol/control/Control'

function createPinToolControl(onClick) {
  const button = document.createElement('button')
  button.innerHTML = '<img class="map-pin-image" src="/map-pin.png" alt="Pin Tool" width="20" height="20"/>';
  button.title = 'Place Pin'
  button.style.padding = '0px'
  button.style.background = '#fff'
  button.style.border = '0px solid #ccc'
  button.style.borderRadius = '0px'
  button.style.marginTop = '0px'
  button.style.cursor = 'pointer'
  button.src = '/map-icon.png'
  button.addEventListener('click', onClick)
  const element = document.createElement('div')
  element.className = 'ol-control ol-pin-tool'
  element.appendChild(button)
  return new Control({ element })
}
import { onMounted, ref, onBeforeUnmount } from 'vue'
import 'ol/ol.css'
import Map from 'ol/Map'
import View from 'ol/View'
import TileLayer from 'ol/layer/Tile'
import OSM from 'ol/source/OSM'
import Zoom from 'ol/control/Zoom'
import Attribution from 'ol/control/Attribution'
import { fromLonLat, toLonLat } from 'ol/proj'
import Feature from 'ol/Feature'
import Point from 'ol/geom/Point'
import VectorSource from 'ol/source/Vector'
import VectorLayer from 'ol/layer/Vector'
import Style from 'ol/style/Style'
import Icon from 'ol/style/Icon'

const props = defineProps({
  enablePinTool: { type: Boolean, default: false }
})
const emit = defineEmits(['pin-placed'])

const mapContainer = ref(null)
let mapInstance = null
let pinLayer = null
let pinSource = null

onMounted(() => {
      // Ensure map resizes after mount
      setTimeout(() => {
        if (mapInstance) mapInstance.updateSize();
      }, 0);
    let pinMode = false
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
      ...(props.enablePinTool ? [createPinToolControl(() => {
        pinMode = !pinMode
        // Optionally highlight button when active
        const img = document.querySelector('.map-pin-image')
        if (img)img.src = pinMode ? '/map-pin-selected.png' : '/map-pin.png'
      })] : [])
    ],
  })

  // Pin tool setup
  if (props.enablePinTool) {
    pinSource = new VectorSource()
    pinLayer = new VectorLayer({
      source: pinSource,
      style: new Style({
        image: new Icon({
          src: '/map-pin-selected.png',
          anchor: [0.5, 1],
          scale: 1.2
        })
      })
    })
    mapInstance.addLayer(pinLayer)

    mapInstance.on('click', function (evt) {
      if (!pinMode) return
      pinSource.clear()
      const coords = evt.coordinate
      const feature = new Feature({
        geometry: new Point(coords)
      })
      pinSource.addFeature(feature)
      const [lon, lat] = toLonLat(coords)
      emit('pin-placed', { lat, lon })
    })
  }
})

onBeforeUnmount(() => {
  if (mapInstance) {
    mapInstance.setTarget(null)
    mapInstance = null
    if (pinLayer) {
      mapInstance.removeLayer(pinLayer)
      pinLayer = null
      pinSource = null
    }
  }
})
</script>

<style scoped>
.ol-pin-tool {
  position: absolute;
  left: 8px;
  top: 60px;
  z-index: 1001;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.ol-map {
  width: 100%;
  height: 100%;
  min-height: 400px;
  border: 1px solid #ccc;
  :deep(.ol-viewport) {
    height: 400px !important;
    min-height: 400px !important;
  }

  :global(.ol-pin-tool) {
    position: absolute;
    left: 8px;
    top: 60px;
    z-index: 1001;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
  }
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
