/**
 * Copyright (c) 2016, Kevin Lewi
 * 
 * Permission to use, copy, modify, and/or distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
 * REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
 * FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
 * INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
 * LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
 * OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
 * PERFORMANCE OF THIS SOFTWARE.
 */

#ifndef _CRYPTORAND_H_
#define _CRYPTORAND_H_

#define _GNU_SOURCE /* for fmemopen() */

#define AES_ALGORITHM EVP_aes_256_ctr()
#define DEFAULT_SEED "12345678901234567890123456789012"

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <gmp.h>
#include <mpfr.h>
#include <openssl/evp.h>
#include <openssl/sha.h>
#include "../flint/fmpz.h"

extern int errno;

/**
 * Contains the state of a cryptorand_t type
 */ 
typedef struct _cryptorand_state_struct {
  char cryptorand_init;
  unsigned long ctr; // used to increment IV
  EVP_CIPHER_CTX *ctx;
  unsigned char key[SHA256_DIGEST_LENGTH];
  unsigned char *iv;
} cryptorand_t[1];

/**
 * Initializes a cryptorand_t type. The default seed is used.
 *
 * @param state The uninitialized state
 * @return void
 */
void cryptorand_init(cryptorand_t state);

/**
 * Initializes a cryptorand_t type with a seed string and a tweak string.
 *
 * @param state The uninitialized state
 * @param seed A string used for the seed
 * @param additional The "tweak", which can be determininistically chosen
 * @return void
 */
void cryptorand_initseed(cryptorand_t state, char *seed, char *additional);

/**
 * Clears the cryptorand_t type.
 *
 * @param state The state to clear
 * @return void
 */
void cryptorand_clear(cryptorand_t state);

/**
 * Selects a random integer in the range [0,m-1] and stores it into f, which is 
 * an fmpz_t.
 *
 * This function simply calls mpz_urandomb_crypto() and converts the resulting 
 * mpz_t into an fmpz_t.
 *
 * @param f The fmpz_t type to contain the random number
 * @param state The cryptorand_t state to use
 * @param m The modulus
 * @return void
 */
void fmpz_randm_crypto(fmpz_t f, cryptorand_t state, const fmpz_t m);

/**
 * Selects a random integer in the range [0,m-1] and stores it into rop, which 
 * is an mpz_t.
 *
 * When the modulus is not a power of 2, this function performs rejection 
 * sampling until the result is within the range [0,m-1].
 *
 * @param rop The mpz_t type to contain the random number
 * @param state The cryptorand_t state to use
 * @param m The modulus
 * @return void
 */
void mpz_urandomb_crypto(mpz_t rop, cryptorand_t state, mp_bitcnt_t m);

/**
 * Samples n random bits and stores them into rop as an mpz_t.
 *
 * @param rop The resutling mpz_t to contain the number [0,2^n-1].
 * @param state The cryptorand_t state to use
 * @param n The number of random bits to sample
 * @return void
 */
void mpz_urandomm_crypto(mpz_t rop, cryptorand_t state, const mpz_t n);


#endif /* _CRYPTORAND_H_ */
