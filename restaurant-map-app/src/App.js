import React, { useState, useEffect } from 'react';
import mapboxgl from 'mapbox-gl';
import * as turf from '@turf/turf';
import './App.css';

mapboxgl.accessToken = 'pk.eyJ1IjoibWloaXJqcGF0ZWwiLCJhIjoiY2xmenJzem9uMGZoMTNzb2M5d2FsZjNuOCJ9.gW_Zx6DA-S_LyiJqGhKobQ';

const Map = () => {
    const [restaurants, setRestaurants] = useState([]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch('http://localhost:8000/api/restaurants/');
                if (response.ok) {
                    const data = await response.json();
                    setRestaurants(data);
                } else {
                    throw new Error('Network response was not ok.');
                }
            } catch (error) {
                console.error('There was a problem with the fetch operation:', error);
            }

        };

        fetchData();
    }, []);

    useEffect(() => {
        const map = new mapboxgl.Map({
            container: 'map-container',
            style: 'mapbox://styles/mapbox/outdoors-v11',
            center: [-97.3647629, 32.7274088],
            zoom: 12,
        });

    map.on('load', () => {
        map.setFilter('poi-label', ['!=', 'category_en', 'Restaurant'])
        map.addSource('restaurants', {
            type: 'geojson',
            data: {
                type: 'FeatureCollection',
                features: restaurants.map((restaurant) => ({
                    type: 'Feature',
                    geometry: {
                        type: 'Point',
                        coordinates: [restaurant.longitude, restaurant.latitude],
                    },
                    properties: {
                        title: restaurant.name,
                        ratings: restaurant.avg_rating,
                    },
                })),
            },
        });

        map.addLayer({
            id: 'restaurants',
            type: 'symbol',
            source: 'restaurants',
            layout: {
                'icon-image': 'restaurant-15',
                'icon-allow-overlap': true,
                'text-field': ['get', 'title'],
                'text-font': ['Open Sans Semibold', 'Arial Unicode MS Bold'],
                'text-size': 14,
                'text-offset': [0, 0.6],
                'text-anchor': 'top',
            },
        });


        map.on('mouseenter', 'restaurants', (e) => {
            map.getCanvas().style.cursor = 'pointer';
            const properties = e.features[0].properties;

            const tooltipContent = `
                <div class="mapboxgl-popup-content">
                    <h4>${properties.title}</h4>
                    <p>Average rating: ${properties.ratings}</p>
                </div>
            `;

            const tooltip = new mapboxgl.Popup()
                                .setLngLat(e.lngLat)
                                .setHTML(tooltipContent)
                                .addTo(map);

            map._tooltip = tooltip;
        });

        map.on('mouseleave', 'restaurants', () => {
            map.getCanvas().style.cursor = '';
            if (map._tooltip) {
                map._tooltip.remove();
                delete map._tooltip;
            }
            map.setFeatureState({ source: 'restaurants', id: null }, { hover: false });
        });


        const circle = turf.circle(
                        [-97.3647629, 32.7274088],
                        2.5,
                        {
                            steps: 64,
                            units: 'miles',
                        }
        );

        map.addLayer({
            id: 'circle',
            type: 'fill',
            source: {
                type: 'geojson',
                data: circle
            },
            paint: {
                'fill-color': '#f03b20',
                'fill-opacity': 0.2
            }
        });

        map.addLayer({
            id: 'center-mark',
            type: 'circle',
            source: {
                type: 'geojson',
                data: {
                    type: 'Feature',
                    geometry: {
                        type: 'Point',
                        coordinates: [-97.3647629, 32.7274088],
                    },
                },
            },
            paint: {
                'circle-radius': 8,
                'circle-color': '#FF4136',
            },
        });


    });


    return () => {
        map.remove();
    };

    }, [restaurants]);

    return (
        <div id="map-container" style={{ width: '100%', height: '500px' }} />
    );
};

export default Map;