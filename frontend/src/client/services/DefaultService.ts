/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PostCreateInput } from '../models/PostCreateInput';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class DefaultService {

    /**
     * Root
     * @returns any Successful Response
     * @throws ApiError
     */
    public static root(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/',
        });
    }

    /**
     * Health
     * @returns any Successful Response
     * @throws ApiError
     */
    public static health(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/health',
        });
    }

    /**
     * Get Posts
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getPosts(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/posts',
        });
    }

    /**
     * Create Post
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static createPost(
        requestBody: PostCreateInput,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/posts',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Authenticate
     * @param next
     * @param ticket
     * @returns any Successful Response
     * @throws ApiError
     */
    public static authenticate(
        next?: string,
        ticket?: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/auth/login',
            query: {
                'next': next,
                'ticket': ticket,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Check Auth
     * @returns any Successful Response
     * @throws ApiError
     */
    public static checkAuth(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/auth/check',
        });
    }

}
